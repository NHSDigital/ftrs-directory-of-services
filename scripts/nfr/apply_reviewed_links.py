#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Any, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[2]
NFRS_ROOT = ROOT / "requirements" / "nfrs"


def load_yaml(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def dump_yaml(p: Path, data: Dict[str, Any]) -> None:
    with p.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def index_nfrs(domain_data: Dict[str, Dict[str, Any]]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    idx: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for dom, data in domain_data.items():
        for nfr in data.get("nfrs", []):
            code = (nfr.get("code") or "").strip()
            if code:
                # IMPORTANT: index references within domain_data so mutations persist
                idx[(dom, code)] = nfr
    return idx


def ensure_story(nfr: Dict[str, Any], key: str) -> bool:
    stories = nfr.get("stories")
    if stories is None:
        nfr["stories"] = [key]
        return True
    if key not in stories:
        stories.append(key)
        return True
    return False


def read_review_csv(p: Path) -> List[Tuple[str, str, str]]:
    # CSV header: key,domain,code
    rows: List[Tuple[str, str, str]] = []
    with p.open("r", encoding="utf-8") as f:
        r = csv.reader(f)
        for i, parts in enumerate(r):
            if i == 0 and parts and parts[0].lower() == "key":
                continue
            if len(parts) < 3:
                continue
            key, domain, code = parts[0].strip(), parts[1].strip(), parts[2].strip()
            rows.append((key, domain, code))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply reviewed Jira→NFR links")
    ap.add_argument("review_csv", help="CSV of approved links: key,domain,code")
    ap.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = ap.parse_args()

    review_path = Path(args.review_csv)
    if not review_path.exists():
        raise SystemExit(f"Review file not found: {review_path}")

    approved = read_review_csv(review_path)
    # Load all domain files first
    domain_files: Dict[str, Path] = {}
    domain_data: Dict[str, Dict[str, Any]] = {}
    for domain_dir in NFRS_ROOT.iterdir():
        if domain_dir.is_dir():
            f = domain_dir / "nfrs.yaml"
            if f.exists():
                domain_files[domain_dir.name] = f
                domain_data[domain_dir.name] = load_yaml(f)

    # Build index referencing domain_data structures
    idx = index_nfrs(domain_data)

    applied = 0
    skipped_missing = 0
    skipped_existing = 0

    for key, domain, code in approved:
        bucket = (domain, code)
        nfr = idx.get(bucket)
        if not nfr:
            skipped_missing += 1
            print(f"Skip {key}: missing NFR {domain}:{code}")
            continue
        if not ensure_story(nfr, key):
            skipped_existing += 1
            print(f"Skip {key}: already linked to {domain}:{code}")
            continue
        applied += 1
        print(f"Apply {key} -> {domain}:{code}")

    if args.dry_run:
        print(f"Dry-run complete: applied={applied}, already={skipped_existing}, missing={skipped_missing}")
        return

    # Write back all domain files
    for dom, path in domain_files.items():
        dump_yaml(path, domain_data[dom])
    print(f"Done: applied={applied}, already={skipped_existing}, missing={skipped_missing}")


if __name__ == "__main__":
    main()
