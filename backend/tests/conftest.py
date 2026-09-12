from pathlib import Path

import pytest
from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env", override=False)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        path = Path(str(item.fspath))
        if "tests/integration" in path.as_posix():
            item.add_marker(pytest.mark.integration)
        elif "tests/unit" in path.as_posix():
            item.add_marker(pytest.mark.unit)
