#!/usr/bin/env python3
"""Test script: start a long-running Trino query, poll its status, then cancel it.

This script verifies that cancelling a query from the client side also
terminates it on the Trino server.

Usage:
    # Uses the same env vars as trino-mcp (TRINO_HOST, TRINO_PORT, etc.)
    python examples/test_async_query_cancel.py

    # Override the timeout (default 10s)
    CANCEL_AFTER_SECONDS=15 python examples/test_async_query_cancel.py
"""

import json
import os
import sys
import threading
import time

# Allow running from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from trino_mcp.config import load_config

import trino

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CANCEL_AFTER_SECONDS = int(os.getenv("CANCEL_AFTER_SECONDS", "20"))
POLL_INTERVAL_SECONDS = 1

# A deliberately slow query – large sequence cross-joined to keep Trino busy.
# Adjust the sequence size if it finishes too quickly on your cluster.
LONG_RUNNING_QUERY = """
SELECT 1 FROM delta.suez.metadata_current
"""


def _make_connection(cfg):
    """Create a fresh Trino DBAPI connection from a TrinoConfig."""
    return trino.dbapi.connect(
        host=cfg.host,
        port=cfg.port,
        user=cfg.user,
        catalog=cfg.catalog or "system",
        schema=cfg.schema or "runtime",
        http_scheme=cfg.http_scheme,
        auth=cfg.auth,
        **(cfg.additional_kwargs or {}),
    )


def _run_query(cursor, query, result_holder):
    """Execute the query in a background thread; store result or exception."""
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        result_holder["rows"] = rows
    except Exception as exc:
        result_holder["error"] = exc


def _get_query_status(monitor_conn, query_id):
    """Look up a query's state in system.runtime.queries."""
    cur = monitor_conn.cursor()
    cur.execute(
        "SELECT state, error_type "
        "FROM system.runtime.queries "
        "WHERE query_id = '" + query_id.replace("'", "''") + "'"
    )
    rows = cur.fetchall()
    if rows:
        return {"state": rows[0][0], "error_type": rows[0][1]}
    return None


def main():
    print(f"Loading Trino config from environment …")
    cfg = load_config()
    print(f"  host={cfg.host}  port={cfg.port}  user={cfg.user}")
    print(f"  cancel after {CANCEL_AFTER_SECONDS}s\n")

    # Two connections: one for the long query, one for monitoring.
    query_conn = _make_connection(cfg)
    monitor_conn = _make_connection(cfg)

    cursor = query_conn.cursor()
    result_holder: dict = {}

    # -----------------------------------------------------------------------
    # 1. Start the long query in a background thread
    # -----------------------------------------------------------------------
    print("Starting long-running query …")
    thread = threading.Thread(
        target=_run_query,
        args=(cursor, LONG_RUNNING_QUERY, result_holder),
        daemon=True,
    )
    thread.start()

    # Wait a moment for Trino to register the query and assign a query_id.
    for _ in range(30):
        time.sleep(0.5)
        if cursor.query_id:
            break
    else:
        print("ERROR: query_id was not assigned within 15 s – aborting.")
        sys.exit(1)

    query_id = cursor.query_id
    print(f"  query_id = {query_id}")

    # -----------------------------------------------------------------------
    # 2. Poll query status until the timeout expires
    # -----------------------------------------------------------------------
    deadline = time.monotonic() + CANCEL_AFTER_SECONDS
    poll_count = 0
    while time.monotonic() < deadline:
        status = _get_query_status(monitor_conn, query_id)
        poll_count += 1
        state = status["state"] if status else "UNKNOWN"
        elapsed = CANCEL_AFTER_SECONDS - (deadline - time.monotonic())
        print(f"  [{elapsed:5.1f}s] poll #{poll_count}: state={state}")

        if state in ("FINISHED", "FAILED"):
            error_type = status.get("error_type") if status else None
            print(f"\nQuery ended before timeout with state={state}, "
                  f"error_type={error_type}.")
            if error_type == "EXCEEDED_TIME_LIMIT":
                print("SUCCESS: Server-side session timeout (query_max_run_time) worked!")
                sys.exit(0)
            print("Hint: increase the sequence size in LONG_RUNNING_QUERY "
                  "if the query finishes too fast.")
            sys.exit(0 if state == "FINISHED" else 1)

        time.sleep(POLL_INTERVAL_SECONDS)

    # -----------------------------------------------------------------------
    # 3. Cancel the query
    # -----------------------------------------------------------------------
    print(f"\nTimeout reached ({CANCEL_AFTER_SECONDS}s). Cancelling query …")
    cursor.cancel()

    # -----------------------------------------------------------------------
    # 4. Verify cancellation on the Trino side
    # -----------------------------------------------------------------------
    print("Waiting for Trino to reflect cancellation …")
    verified = False
    for attempt in range(10):
        time.sleep(1)
        status = _get_query_status(monitor_conn, query_id)
        state = status["state"] if status else "UNKNOWN"
        error_type = status.get("error_type") if status else None
        print(f"  verification attempt {attempt + 1}: state={state}, "
              f"error_type={error_type}")
        if state == "FAILED" and error_type == "USER_CANCELED":
            verified = True
            break
        if state in ("FAILED", "FINISHED"):
            # Some other terminal state
            break

    # Wait for the thread to finish (it should raise / return quickly now)
    thread.join(timeout=5)

    # -----------------------------------------------------------------------
    # 5. Report results
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    if verified:
        print("SUCCESS: Query was cancelled and Trino reports "
              "state=FAILED, error_type=USER_CANCELED.")
    else:
        print(f"FAILURE: Expected state=FAILED/error_type=USER_CANCELED "
              f"but got state={state}, error_type={error_type}")

    if "error" in result_holder:
        print(f"  Client-side exception: {result_holder['error']}")
    elif "rows" in result_holder:
        print(f"  Client-side rows (unexpected): {result_holder['rows']}")

    print("=" * 60)
    sys.exit(0 if verified else 1)


if __name__ == "__main__":
    main()
