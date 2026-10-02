from types import SimpleNamespace
from unittest.mock import MagicMock

import run_instagram_snapshots as job


def test_main_exits_zero_when_all_captures_succeed(monkeypatch):
    capture = MagicMock()
    capture.execute_all.return_value = SimpleNamespace(captured=3, failed=0)
    container = MagicMock()
    container.capture_instagram_followers.return_value = capture
    monkeypatch.setattr(job, "get_dependency_container", lambda: container)

    assert job.main() == 0


def test_main_exits_nonzero_when_any_capture_fails(monkeypatch):
    capture = MagicMock()
    capture.execute_all.return_value = SimpleNamespace(captured=2, failed=1)
    container = MagicMock()
    container.capture_instagram_followers.return_value = capture
    monkeypatch.setattr(job, "get_dependency_container", lambda: container)

    assert job.main() == 1
