#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    raise SystemExit("scikit-learn is required. Install with: pip install scikit-learn")

ROOT = Path(__file__).resolve().parents[2]
BACKLOG_DIR = ROOT / "requirements" / "user-stories" / "backlog" / "jira"
NFRS_ROOT = ROOT / "requirements" / "nfrs"


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def load_yaml(p: Path) -> Dict[str, Any]:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def dump_yaml(p: Path, data: Dict[str, Any]) -> None:
    p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def collect_nfr_labels() -> Tuple[List[Tuple[str, str, str]], Dict[str, Dict[str, Any]], Dict[str, Path]]:
    labels: List[Tuple[str, str, str]] = []  # (domain, code, text)
    domain_files: Dict[str, Path] = {}
    domain_data: Dict[str, Dict[str, Any]] = {}
    for domain_dir in NFRS_ROOT.iterdir():
        if not domain_dir.is_dir():
            continue
        f = domain_dir / "nfrs.yaml"
        if not f.exists():
            continue
        dom = domain_dir.name
        domain_files[dom] = f
        data = load_yaml(f)
        domain_data[dom] = data
        for n in data.get("nfrs", []) or []:
            code = (n.get("code") or "").strip()
            req = (n.get("requirement") or "").strip()
            expl = (n.get("explanation") or "").strip()
            text = f"{dom} {code} {req}. {expl}"
            labels.append((dom, code, text))
    return labels, domain_data, domain_files


def build_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2), min_df=1)


def prepare_story_text(md: str) -> str:
    t = re.sub(r"```[\s\S]*?```", " ", md)
    t = re.sub(r"</?details>|</?summary>", " ", t, flags=re.IGNORECASE)
    t = re.sub(r"^\*\*Metadata\*\*[\s\S]*?(?:^#|\Z)", " ", t, flags=re.MULTILINE)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def best_matches(text: str, labels: List[Tuple[str, str, str]], vec: TfidfVectorizer, per_domain: bool, threshold: float, top: int) -> List[Tuple[str, str, float]]:
    corpus = [lbl[2] for lbl in labels] + [text]
    X = vec.fit_transform(corpus)
    sims = cosine_similarity(X[-1], X[:-1]).ravel()
    scored: List[Tuple[str, str, float]] = []
    for i, (dom, code, _) in enumerate(labels):
        s = float(sims[i])
        if s >= threshold:
            scored.append((dom, code, s))
    if not per_domain:
        return sorted(scored, key=lambda x: x[2], reverse=True)[:top]
    best: Dict[str, Tuple[str, str, float]] = {}
    for dom, code, s in scored:
        cur = best.get(dom)
        if cur is None or s > cur[2]:
            best[dom] = (dom, code, s)
    return sorted(best.values(), key=lambda x: x[2], reverse=True)[:top]


def parse_epic_children(epic_md: Path) -> Dict[str, str]:
    if not epic_md.exists():
        raise FileNotFoundError(f"Epic file not found: {epic_md}")
    text = read_text(epic_md)
    # Capture section
    m = re.search(r"^## Issues in this Epic\n([\s\S]*?)(?:^## |\Z)", text, flags=re.MULTILINE)
    if not m:
        return {}
    section = m.group(1)
    result: Dict[str, str] = {}
    for line in section.splitlines():
        # Line like: - [FTRS-123](...) – summary ...
        km = re.search(r"\bFTRS-\d+\b", line)
        if km:
            key = km.group(0).upper()
            # Remove link markdown and keep the trailing summary text
            cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)", key, line)
            cleaned = cleaned.strip(" -–—:")
            result[key] = cleaned
    return result


def list_perf_ops_for_service(domain_data: Dict[str, Dict[str, Any]], service: str) -> List[str]:
    ops: Set[str] = set()
    perf = domain_data.get("performance") or {}
    for n in (perf.get("nfrs") or []):
        for op in (n.get("operations") or []):
            if str(op.get("service","")) == service:
                oid = str(op.get("operation_id",""))
                if oid:
                    ops.add(oid)
    return sorted(ops)


def choose_operation_for_story(text: str, candidate_ops: List[str]) -> Optional[str]:
    t = text.lower()
    # direct exact op id mention
    for oid in candidate_ops:
        if oid.lower() in t:
            return oid
    # simple heuristics for common dos-search ops
    if "ods" in t and ("lookup" in t or "code" in t):
        for oid in candidate_ops:
            if "lookup" in oid or "ods" in oid:
                return oid
    if "nearby" in t or "geo" in t:
        for oid in candidate_ops:
            if "nearby" in oid:
                return oid
    if "search" in t:
        for oid in candidate_ops:
            if "search" in oid:
                return oid
    return None


def ensure_list(d: Dict[str, Any], key: str) -> List[str]:
    arr = d.get(key)
    if not isinstance(arr, list):
        arr = []
        d[key] = arr
    return arr


def main() -> None:
    ap = argparse.ArgumentParser(description="Map epic child issues to NFR YAMLs (NFR-level or operation-level)")
    ap.add_argument("--epic", required=True, help="Epic key, e.g., FTRS-1365")
    ap.add_argument("--service", default="dos-search", help="Service id for operation mapping (default: dos-search)")
    ap.add_argument("--threshold", type=float, default=0.05)
    ap.add_argument("--top", type=int, default=1)
    ap.add_argument("--per-domain", action="store_true")
    ap.add_argument("--default-perf-nfr", default=None, help="Fallback performance NFR code (e.g., PERF-001) for unmatched issues")
    ap.add_argument("--default-operation-id", default=None, help="Fallback operation_id (e.g., dos-lookup-ods) for unmatched issues when default-perf-nfr is set")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    labels, domain_data, domain_files = collect_nfr_labels()
    vec = build_vectorizer()
    epic_path = BACKLOG_DIR / f"{args.epic}.md"
    child_map = parse_epic_children(epic_path)
    if not child_map:
        print(f"No child issues found in {epic_path}")
        return

    # Prepare perf ops for selected service
    perf_ops = list_perf_ops_for_service(domain_data, args.service)

    updates_nfr_level: Dict[str, List[str]] = {}
    updates_op_level: Dict[Tuple[str,str], List[str]] = {}  # (service, op_id) -> keys

    unmatched: List[str] = []
    for key in child_map.keys():
        md_file = BACKLOG_DIR / f"{key}.md"
        if not md_file.exists():
            print(f"Skip {key}: not in cache {md_file}")
            continue
        raw = read_text(md_file)
        story_text = prepare_story_text(raw)
        if len(story_text) < 40:
            # Fallback to the summary line from the epic list
            story_text = child_map.get(key, story_text)
        matches = best_matches(story_text, labels, vec, per_domain=args.per_domain, threshold=args.threshold, top=args.top)
        if not matches:
            print(f"{key}: no NFR match >= {args.threshold}")
            unmatched.append(key)
            continue
        dom, code, score = matches[0]
        print(f"{key}: {dom}:{code} ({score:.3f})")
        # If performance domain and code is one of op-specific NFRs, try operation mapping
        if dom == "performance" and code in {"PERF-001", "PERF-011", "PERF-012", "PERF-013"} and perf_ops:
            oid = choose_operation_for_story(story_text, perf_ops)
            if oid:
                updates_op_level.setdefault((args.service, oid), []).append(key)
                continue
        updates_nfr_level.setdefault(f"{dom}:{code}", []).append(key)

    # Dry-run preview
    print("\nPlanned updates:")
    for bucket, keys in sorted(updates_nfr_level.items()):
        print(f"- NFR {bucket}: +{len(set(keys))} -> {sorted(set(keys))}")
    for (svc, oid), keys in sorted(updates_op_level.items()):
        print(f"- Operation {svc}/{oid}: +{len(set(keys))} -> {sorted(set(keys))}")

    # Consider unmatched fallbacks for performance op mapping
    if unmatched and args.default_perf_nfr and args.default_operation_id:
        print(f"\nApplying fallback for {len(unmatched)} unmatched issues -> performance:{args.default_perf_nfr} at operation {args.service}/{args.default_operation_id}")
        updates_op_level.setdefault((args.service, args.default_operation_id), []).extend(unmatched)

    if not args.write:
        print("\nDry-run only. Re-run with --write to apply.")
        return

    # Apply NFR-level updates
    for dom_code, keys in updates_nfr_level.items():
        dom, code = dom_code.split(":", 1)
        data = domain_data.get(dom)
        if not data:
            continue
        for n in data.get("nfrs", []) or []:
            if n.get("code") == code:
                arr = ensure_list(n, "stories")
                for k in keys:
                    if k not in arr:
                        arr.append(k)
                break
    # Apply operation-level updates under performance
    perf_data = domain_data.get("performance") or {}
    for (svc, oid), keys in updates_op_level.items():
        for n in perf_data.get("nfrs", []) or []:
            for op in (n.get("operations") or []):
                if str(op.get("service")) == svc and str(op.get("operation_id")) == oid:
                    arr = ensure_list(op, "stories")
                    for k in keys:
                        if k not in arr:
                            arr.append(k)
    # Persist
    for dom, path in domain_files.items():
        dump_yaml(path, domain_data[dom])
    print("Applied updates to NFR YAMLs.")


if __name__ == "__main__":
    main()
