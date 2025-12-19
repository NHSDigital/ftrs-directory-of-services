#!/usr/bin/env python3
from __future__ import annotations
import os
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts" / "nfr"

REFRESH_SIMPLIFIED = SCRIPTS_DIR / "refresh_simplified_nfr_page.py"
BUILD_SERVICE = SCRIPTS_DIR / "build_service_pages.py"
BUILD_TEAM_RELEASE_OP = SCRIPTS_DIR / "build_team_release_operation_pages.py"


def python_bin() -> str:
    """Choose a Python with required deps.

    Preference order:
    1) Workspace venv at .venv/bin/python
    2) Current interpreter (sys.executable)
    3) Homebrew python3 if present
    4) Fallback to 'python3' from PATH
    """
    venv_py = ROOT / ".venv" / "bin" / "python"
    if venv_py.exists():
        return str(venv_py)
    if sys.executable:
        return sys.executable
    brew_py = "/opt/homebrew/bin/python3"
    return brew_py if Path(brew_py).exists() else (os.environ.get("PYTHON", "python3"))


def run_script(path: Path) -> None:
    cmd = [python_bin(), str(path)]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> None:
    # 1) Generate domain pages and simplified index (this script has its own deps)
    run_script(REFRESH_SIMPLIFIED)
    # 2) Generate per-service pages and insert links into simplified index
    run_script(BUILD_SERVICE)
    # 3) Generate per-team, per-release, and per-operation views
    run_script(BUILD_TEAM_RELEASE_OP)
    print("Completed: domain pages, simplified index, per-service pages, and team/release/operation views")


if __name__ == "__main__":
    main()
