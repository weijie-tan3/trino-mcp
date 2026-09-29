"""End-to-end shutdown tests for the stdio server (issue #60).

Each test launches the real server as a subprocess, completes the MCP
handshake, then stops it the way an MCP client might. The server must exit
promptly without hanging or aborting in ``_enter_buffered_busy``.
"""

import json
import os
import selectors
import signal
import subprocess
import sys
import time
from contextlib import contextmanager

import pytest

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="POSIX signals only")

INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "shutdown-test", "version": "1"},
    },
}

HANDSHAKE_TIMEOUT = 15


def _readline_with_timeout(pipe, timeout: float) -> bytes:
    """Read one line from ``pipe`` without blocking past ``timeout``."""
    selector = selectors.DefaultSelector()
    selector.register(pipe, selectors.EVENT_READ)
    try:
        deadline = time.monotonic() + timeout
        buf = bytearray()
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not selector.select(remaining):
                raise TimeoutError(f"no handshake response within {timeout}s")
            chunk = os.read(pipe.fileno(), 1)
            if not chunk:
                raise EOFError("server closed stdout before responding")
            buf += chunk
            if chunk == b"\n":
                return bytes(buf)
    finally:
        selector.close()


@contextmanager
def _running_server():
    """Start the server and guarantee it is killed/reaped, even on setup failure."""
    env = {**os.environ, "AUTH_METHOD": "NONE", "TRINO_HOST": "localhost"}
    proc = subprocess.Popen(
        [sys.executable, "-m", "trino_mcp", "--auth-method", "NONE"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    try:
        proc.stdin.write((json.dumps(INIT) + "\n").encode())
        proc.stdin.flush()
        line = _readline_with_timeout(proc.stdout, HANDSHAKE_TIMEOUT)
        response = json.loads(line)
        assert response["id"] == 1
        time.sleep(0.3)
        yield proc
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()


def _wait(proc, timeout=10):
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        pytest.fail("server hung during shutdown")
    stderr = proc.stderr.read().decode(errors="replace")
    assert "Fatal Python error" not in stderr, stderr
    return proc.returncode


@pytest.mark.parametrize(
    "signame,expected", [("SIGINT", 130), ("SIGTERM", 143), ("SIGHUP", 129)]
)
def test_signal_with_stdin_open_exits_cleanly(signame, expected):
    with _running_server() as proc:
        proc.send_signal(getattr(signal, signame))
        assert _wait(proc) == expected


def test_stdin_eof_exits_cleanly():
    with _running_server() as proc:
        proc.stdin.close()
        assert _wait(proc) == 0

