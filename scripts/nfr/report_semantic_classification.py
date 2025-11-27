#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import defaultdict
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "scans" / "nfr" / "semantic"
INPUT = REPORT_DIR / "all_matches.csv"
OUT_SUMMARY = REPORT_DIR / "summary_per_nfr.csv"
OUT_TOP = REPORT_DIR / "top_matches.csv"
OUT_MD = REPORT_DIR / "proposed-links.md"
OUT_NEW_ONLY = REPORT_DIR / "new_only_matches.csv"
OUT_DUPES = REPORT_DIR / "already_linked.csv"
NFRS_ROOT = ROOT / "requirements" / "nfrs"


@dataclass
class Row:
    key: str
    domain: str
    code: str
    score: float


def read_rows(p: Path) -> List[Row]:
    rows: List[Row] = []
    if not p.exists():
        return rows
    with p.open("r", encoding="utf-8") as f:
        r = csv.reader(f)
        for parts in r:
            if len(parts) < 4:
                continue
            key, domain, code, score = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
            try:
                rows.append(Row(key=key, domain=domain, code=code, score=float(score)))
            except ValueError:
                continue
    return rows


def write_summary_per_nfr(rows: List[Row], out_path: Path) -> None:
    # Aggregate by domain+code
    agg: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    for r in rows:
        agg[(r.domain, r.code)].append(r.score)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["domain", "code", "count", "max_score", "avg_score"])  # header
        for (domain, code), scores in sorted(agg.items(), key=lambda x: (-len(x[1]), -max(x[1]))):
            count = len(scores)
            max_s = max(scores)
            avg_s = sum(scores) / count
            w.writerow([domain, code, count, f"{max_s:.6f}", f"{avg_s:.6f}"])


def write_top_sorted(rows: List[Row], out_path: Path, limit: int | None = None) -> None:
    sorted_rows = sorted(rows, key=lambda r: r.score, reverse=True)
    if limit is not None:
        sorted_rows = sorted_rows[:limit]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "domain", "code", "score"])  # header
        for r in sorted_rows:
            w.writerow([r.key, r.domain, r.code, f"{r.score:.6f}"])


def write_markdown(rows: List[Row], out_path: Path) -> None:
    # Group by domain then by code
    by_domain: Dict[str, Dict[str, List[Row]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_domain[r.domain][r.code].append(r)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("# Proposed Links (Semantic Classifier)\n\n")
        f.write("Note: Scores are cosine similarities (TF-IDF). Treat these as suggestions for human review; do not merge blindly.\n\n")
        for domain in sorted(by_domain.keys()):
            f.write(f"## {domain.capitalize()}\n\n")
            codes = by_domain[domain]
            for code in sorted(codes.keys()):
                f.write(f"### {code}\n\n")
                # Sort entries for this code by score desc
                entries = sorted(codes[code], key=lambda r: r.score, reverse=True)
                for r in entries:
                    f.write(f"- {r.key} – score {r.score:.3f}\n")
                f.write("\n")


def load_existing_links() -> Dict[Tuple[str, str], set[str]]:
    existing: Dict[Tuple[str, str], set[str]] = {}
    for domain_dir in NFRS_ROOT.iterdir():
        if not domain_dir.is_dir():
            continue
        f = domain_dir / "nfrs.yaml"
        if not f.exists():
            continue
        with f.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        for nfr in (data.get("nfrs") or []):
            code = (nfr.get("code") or "").strip()
            stories = set((nfr.get("stories") or []))
            if code:
                existing[(domain_dir.name, code)] = stories
    return existing


def split_new_vs_existing(rows: List[Row]) -> tuple[List[Row], List[Row]]:
    existing = load_existing_links()
    new_rows: List[Row] = []
    dup_rows: List[Row] = []
    for r in rows:
        bucket = (r.domain, r.code)
        already = r.key in existing.get(bucket, set())
        if already:
            dup_rows.append(r)
        else:
            new_rows.append(r)
    return new_rows, dup_rows


def main() -> None:
    rows = read_rows(INPUT)
    if not rows:
        print(f"No input rows found in {INPUT}")
        return
    # Generate filtered sets
    new_rows, dup_rows = split_new_vs_existing(rows)
    write_summary_per_nfr(rows, OUT_SUMMARY)
    write_top_sorted(rows, OUT_TOP, limit=None)  # all sorted
    write_markdown(rows, OUT_MD)
    # Write filtered CSVs
    write_top_sorted(new_rows, OUT_NEW_ONLY, limit=None)
    write_top_sorted(dup_rows, OUT_DUPES, limit=None)
    print(f"Wrote: {OUT_SUMMARY}\nWrote: {OUT_TOP}\nWrote: {OUT_MD}\nWrote (new-only): {OUT_NEW_ONLY}\nWrote (already-linked): {OUT_DUPES}")


if __name__ == "__main__":
    main()
