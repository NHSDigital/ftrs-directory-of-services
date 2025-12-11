#!/usr/bin/env python3
from __future__ import annotations
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts" / "nfr"

REFRESH_SIMPLIFIED = SCRIPTS_DIR / "refresh_simplified_nfr_page.py"
BUILD_SERVICE = SCRIPTS_DIR / "build_service_pages.py"


def python_bin() -> str:
    # Prefer Homebrew python path (matches prior successful runs), fallback to env python
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
    print("Completed: domain pages, simplified index, and per-service pages")


if __name__ == "__main__":
    main()
