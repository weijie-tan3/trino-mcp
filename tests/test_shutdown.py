"""End-to-end shutdown tests for the stdio server (issue #60).

Each test launches the real server as a subprocess, completes the MCP
handshake, then stops it the way an MCP client might. The server must exit
promptly without hanging or aborting in ``_enter_buffered_busy``.
"""

import json
import os
import signal
import subprocess
import sys
import time

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


def _start_server():
    env = {**os.environ, "AUTH_METHOD": "NONE", "TRINO_HOST": "localhost"}
    proc = subprocess.Popen(
        [sys.executable, "-m", "trino_mcp", "--auth-method", "NONE"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    proc.stdin.write((json.dumps(INIT) + "\n").encode())
    proc.stdin.flush()
    response = json.loads(proc.stdout.readline())
    assert response["id"] == 1
    time.sleep(0.3)
    return proc


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
    proc = _start_server()
    proc.send_signal(getattr(signal, signame))
    assert _wait(proc) == expected


def test_stdin_eof_exits_cleanly():
    proc = _start_server()
    proc.stdin.close()
    assert _wait(proc) == 0
