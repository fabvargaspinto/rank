import ast
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parents[4] / "core"


def test_application_does_not_import_infrastructure():
    violations = []

    for path in CORE_DIR.rglob("application/*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            else:
                continue

            for module in modules:
                if ".infrastructure" in module or module.endswith("infrastructure"):
                    violations.append(f"{path.relative_to(CORE_DIR)}: {module}")

    assert violations == []
