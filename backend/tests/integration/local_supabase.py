from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

LOCAL_SUPABASE_URL = "http://127.0.0.1:54321"
LOCAL_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9."
    "CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
)
LOCAL_SERVICE_ROLE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0."
    "EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
)
_LOCAL_HOSTS = (
    "127.0.0.1",
    "localhost",
    "host.docker.internal",
    "kong",
    "supabase_kong",
)
_REPO_ROOT = Path(__file__).resolve().parents[3]
_TEST_ENCRYPTION_KEY = "00" * 32
_TEST_HMAC_KEY = "11" * 32
_START_TIMEOUT_SECONDS = 180


def configure_local_supabase_env() -> str:
    current = os.getenv("SUPABASE_URL", "").strip()
    url = current if _is_local_url(current) else LOCAL_SUPABASE_URL
    os.environ["SUPABASE_URL"] = url
    os.environ["SUPABASE_SECRET_KEY"] = LOCAL_SERVICE_ROLE_KEY
    os.environ["SUPABASE_ANON_KEY"] = LOCAL_ANON_KEY
    os.environ["NEXT_PUBLIC_SUPABASE_URL"] = url
    os.environ["NEXT_PUBLIC_SUPABASE_ANON_KEY"] = LOCAL_ANON_KEY
    os.environ.setdefault("EMAIL_ENCRYPTION_KEY", _TEST_ENCRYPTION_KEY)
    os.environ.setdefault("EMAIL_HMAC_KEY", _TEST_HMAC_KEY)
    return url


def ensure_local_supabase_running(url: str) -> bool:
    if is_local_supabase_up(url):
        return True
    if not _start_local_supabase():
        return False
    deadline = time.monotonic() + _START_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if is_local_supabase_up(url):
            return True
        time.sleep(2)
    return False


def is_local_supabase_up(url: str) -> bool:
    health_url = url.rstrip("/") + "/auth/v1/health"
    try:
        with urlopen(health_url, timeout=2) as response:
            return 200 <= response.status < 300
    except (OSError, URLError):
        return False


def _is_local_url(url: str) -> bool:
    return any(host in url for host in _LOCAL_HOSTS)


def _start_local_supabase() -> bool:
    pnpm = shutil.which("pnpm")
    if pnpm is None:
        return False
    result = subprocess.run(
        [
            pnpm,
            "--dir",
            str(_REPO_ROOT / "frontend"),
            "exec",
            "supabase",
            "--workdir",
            str(_REPO_ROOT),
            "start",
            "--yes",
        ],
        cwd=_REPO_ROOT,
        check=False,
    )
    return result.returncode == 0
