#!/usr/bin/env python3
"""Scan nfrs.yaml files for missing explanations or stories.

Outputs a concise checklist to stdout.
"""
from __future__ import annotations
from pathlib import Path
import sys

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    sys.stderr.write("PyYAML is required. Install with: python3 -m pip install pyyaml\n")
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
DOMAINS_DIR = ROOT / "requirements/nfrs"

def main() -> int:
    gaps: list[str] = []
    for yml in sorted(DOMAINS_DIR.glob("*/nfrs.yaml")):
        domain = yml.parent.name
        data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
        for n in (data.get("nfrs") or []):
            code = n.get("code", "UNKNOWN")
            # Explanation gap
            expl = (n.get("explanation") or "").strip()
            if not expl:
                gaps.append(f"[Explanation] {domain} {code} is missing explanation")
            # Stories gap
            stories = n.get("stories") or []
            if not stories:
                gaps.append(f"[Stories] {domain} {code} has no stories mapped")

    if gaps:
        print("Checklist: Missing NFR metadata")
        for g in gaps:
            print(f"- {g}")
        return 1
    else:
        print("No gaps found: all NFRs have explanations and stories.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
