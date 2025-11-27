#!/usr/bin/env python3
"""Migrate legacy NFR sources into per-domain nfrs.yaml files.

Sources:
- requirements/nfrs/cross-references/nfr-matrix.md (codes, domain, stories, anchor requirement)
- requirements/nfrs/cross-references/nfr-explanations.yaml (explanations)
- requirements/nfrs/<domain>/expectations.yaml (controls for control-centric domains)

Creates:
- requirements/nfrs/<domain>/nfrs.yaml for all domains found in the matrix.

Performance domain is already seeded; this script skips migrating operations there.
"""
from __future__ import annotations
from pathlib import Path
import re
import sys
import json

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    sys.stderr.write("PyYAML is required. Install with: python3 -m pip install pyyaml\n")
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "requirements/nfrs/cross-references/nfr-matrix.md"
EXPLANATIONS_FILE = ROOT / "requirements/nfrs/cross-references/nfr-explanations.yaml"
DOMAINS_DIR = ROOT / "requirements/nfrs"

ROW_PATTERN = re.compile(r"^\|\s*([A-Z]+-[0-9]+)\s*\|\s*([A-Za-z]+)\s*\|\s*([^|]*)\|\s*([^|]*)\|")

def parse_matrix_rows(text: str):
    rows = []
    for line in text.splitlines():
        m = ROW_PATTERN.match(line)
        if not m:
            continue
        code, domain, stories, anchor = [x.strip() for x in m.groups()]
        rows.append({"code": code, "domain": domain.lower(), "stories": stories, "anchor": anchor})
    return rows

def load_explanations() -> dict[str,str]:
    exps: dict[str,str] = {}
    if EXPLANATIONS_FILE.exists():
        data = yaml.safe_load(EXPLANATIONS_FILE.read_text(encoding="utf-8")) or {}
        for k, v in (data.get("explanations") or {}).items():
            exps[k] = str(v).strip()
    return exps

def load_controls_registry(domain: str):
    path = DOMAINS_DIR / domain / "expectations.yaml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = data.get("controls", []) or []
    # normalize types and sort
    items.sort(key=lambda c: (c.get("nfr_code", ""), c.get("control_id", "")))
    return items

def main():
    if not MATRIX.exists():
        sys.stderr.write(f"Matrix file not found: {MATRIX}\n")
        return 2
    rows = parse_matrix_rows(MATRIX.read_text(encoding="utf-8"))
    if not rows:
        sys.stderr.write("No rows parsed from matrix.\n")
        return 2
    explanations = load_explanations()
    by_domain: dict[str, list[dict]] = {}
    for r in rows:
        by_domain.setdefault(r["domain"], []).append(r)

    for domain, drows in by_domain.items():
        out_dir = DOMAINS_DIR / domain
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "nfrs.yaml"
        # Build nfrs array
        nfrs = []
        # Controls per domain
        controls = load_controls_registry(domain)
        controls_by_code: dict[str, list[dict]] = {}
        for c in controls:
            code = c.get("nfr_code")
            if not code:
                continue
            controls_by_code.setdefault(code, []).append({
                "control_id": c.get("control_id"),
                "measure": c.get("measure"),
                "threshold": c.get("threshold"),
                "tooling": c.get("tooling"),
                "cadence": c.get("cadence"),
                "environments": c.get("environments"),
                "services": c.get("services"),
                "status": c.get("status"),
                "rationale": c.get("rationale"),
            })
        def sort_key(r):
            prefix, num = r["code"].split("-")
            try:
                return (prefix, int(num))
            except ValueError:
                return (prefix, num)
        for row in sorted(drows, key=sort_key):
            code = row["code"]
            # stories normalization
            stories_raw = row["stories"]
            stories = [s.strip() for s in stories_raw.split(',') if s.strip() and s.strip() != '(none)'] if stories_raw else []
            expl = explanations.get(code, "")
            entry = {
                "code": code,
                "requirement": row["anchor"],
                "explanation": expl,
                "stories": stories
            }
            # controls only for non-performance domains
            if domain != "performance":
                if code in controls_by_code:
                    entry["controls"] = controls_by_code[code]
            # performance operations are managed manually in performance/nfrs.yaml
            nfrs.append(entry)

        doc = {
            "version": 1.0,
            "generated": "auto-migrated",
            "nfrs": nfrs
        }
        out_path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
        print(f"Wrote {out_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
