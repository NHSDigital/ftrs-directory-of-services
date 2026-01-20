import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest


def _find_repo_root(start: Path) -> Path:
    current = start
    for _ in range(10):
        if (current / "pyproject.toml").exists() and (current / "services").exists():
            return current
        current = current.parent
    return start.parents[4]


def _load_workflow_module(module_name: str, rel_path: str) -> Any:
    repo_root = _find_repo_root(Path(__file__).resolve())
    mod_path = repo_root / rel_path
    spec = importlib.util.spec_from_file_location(module_name, str(mod_path))
    if not spec or not spec.loader:
        raise RuntimeError()
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class _DummyResponse:
    def __init__(
        self,
        *,
        status_code: int,
        text: str,
        headers: dict[str, Any] | None,
        reason: str,
    ) -> None:
        self.status_code = status_code
        self._text = text
        self.headers = headers or {}
        self.reason = reason

    @property
    def text(self) -> str:
        return self._text

    @staticmethod
    def json() -> Any:
        return {}


@pytest.fixture
def create_module() -> Any:
    return _load_workflow_module(
        "create_open_search_index", "scripts/workflow/create_open_search_index.py"
    )


@pytest.fixture
def create_populate_module() -> Any:
    return _load_workflow_module(
        "populate_open_search_index", "scripts/workflow/populate_open_search_index.py"
    )


@pytest.fixture
def fake_credentials() -> Any:
    return "creds"


@pytest.fixture
def dummy_response() -> Any:
    def _make_dummy_response(
        status_code: int = 200,
        text: str = "",
        headers: dict[str, Any] | None = None,
        reason: str = "",
    ) -> Any:
        return _DummyResponse(
            status_code=status_code,
            text=text,
            headers=headers,
            reason=reason,
        )

    return _make_dummy_response
