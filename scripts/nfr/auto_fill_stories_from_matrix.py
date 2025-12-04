#!/usr/bin/env python3
"""Auto-fill missing stories in domain nfrs.yaml from the cross-reference matrix.

For each domain nfrs.yaml, if an NFR has empty stories, copy stories from
requirements/nfrs/cross-references/nfr-matrix.md if available.
"""
from __future__ import annotations
from pathlib import Path
import re
import sys

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    sys.stderr.write("PyYAML is required. Install with: python3 -m pip install pyyaml\n")
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "requirements/nfrs/cross-references/nfr-matrix.md"
DOMAINS_DIR = ROOT / "requirements/nfrs"

ROW_PATTERN = re.compile(r"^\|\s*([A-Z]+-[0-9]+)\s*\|\s*([A-Za-z]+)\s*\|\s*([^|]*)\|\s*([^|]*)\|")

def parse_matrix(text: str) -> dict[str, list[str]]:
    """Return map of code -> stories list (normalized, without '(none)')."""
    mapping: dict[str, list[str]] = {}
    for line in text.splitlines():
        m = ROW_PATTERN.match(line)
        if not m:
            continue
        code, _domain, stories_raw, _anchor = [x.strip() for x in m.groups()]
        stories = [s.strip() for s in stories_raw.split(',') if s.strip() and s.strip() != '(none)'] if stories_raw else []
        mapping[code] = stories
    return mapping

def main() -> int:
    if not MATRIX.exists():
        sys.stderr.write(f"Matrix file not found: {MATRIX}\n")
        return 2
    matrix_map = parse_matrix(MATRIX.read_text(encoding="utf-8"))
    changed = 0
    for yml in sorted(DOMAINS_DIR.glob("*/nfrs.yaml")):
        data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
        nfrs = data.get("nfrs") or []
        updated = False
        for n in nfrs:
            code = n.get("code")
            stories = n.get("stories") or []
            if not stories and code in matrix_map and matrix_map[code]:
                n["stories"] = matrix_map[code]
                updated = True
        if updated:
            yml.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            changed += 1
            print(f"Updated stories from matrix: {yml}")
    if changed:
        print(f"Auto-filled stories for {changed} domain files.")
    else:
        print("No changes: either stories already present or matrix has none.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
