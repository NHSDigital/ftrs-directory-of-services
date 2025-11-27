#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Any

import yaml

# Light-weight semantic classifier using TF-IDF cosine similarity.
# Maps Jira backlog Markdown stories to NFR codes based on textual similarity
# to the NFR requirement/explanation texts. Safer than broad keyword grep.

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception as e:  # pragma: no cover
    raise SystemExit(
        "scikit-learn is required. Install with: pip install scikit-learn"
    )


ROOT = Path(__file__).resolve().parents[2]
BACKLOG_DIR = ROOT / "requirements" / "user-stories" / "backlog" / "jira"
NFRS_ROOT = ROOT / "requirements" / "nfrs"


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def load_yaml(p: Path) -> Dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(p: Path, data: Dict[str, Any]) -> None:
    with p.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def strip_html(text: str) -> str:
    # Unescape HTML entities and strip tags
    t = html.unescape(text)
    return re.sub(r"<[^>]+>", " ", t)


def strip_md_sections(text: str) -> str:
    # Remove obvious meta sections that cause noise
    # e.g., code fences, headings like Dependencies, Metadata tables
    t = re.sub(r"```[\s\S]*?```", " ", text)  # code fences
    # Remove collapsible HTML details wrappers
    t = re.sub(r"</?details>|</?summary>", " ", t, flags=re.IGNORECASE)
    # Drop section lines that start with common metadata bullets
    t = re.sub(r"^\s*\*\*Metadata\*\*[\s\S]*?(?:^#|\Z)", " ", t, flags=re.MULTILINE)
    # Remove 'Dependencies' section to avoid resource availability false-positives
    t = re.sub(r"^##\s*Dependencies[\s\S]*?(?:^##\s|\Z)", " ", t, flags=re.IGNORECASE | re.MULTILINE)
    return t


@dataclass
class NFRLabel:
    domain: str
    code: str
    text: str


def collect_nfr_labels() -> Tuple[List[NFRLabel], Dict[str, Dict[str, Any]], Dict[str, Path]]:
    labels: List[NFRLabel] = []
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
        data = load_yaml(f) or {}
        domain_data[dom] = data
        for nfr in data.get("nfrs", []):
            code = nfr.get("code", "").strip()
            req = (nfr.get("requirement") or "").strip()
            expl = (nfr.get("explanation") or "").strip()
            # Build a label text that represents the NFR intent
            text = f"{dom} {code} {req}. {expl}"
            labels.append(NFRLabel(domain=dom, code=code, text=text))

    return labels, domain_data, domain_files


def ensure_story(nfr: Dict[str, Any], key: str) -> bool:
    stories = nfr.get("stories")
    if stories is None:
        nfr["stories"] = [key]
        return True
    if key not in stories:
        stories.append(key)
        return True
    return False


def index_nfrs(domain_data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    idx: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for dom, data in domain_data.items():
        dom_idx: Dict[str, Dict[str, Any]] = {}
        for nfr in data.get("nfrs", []):
            code = nfr.get("code")
            if code:
                dom_idx[code] = nfr
        idx[dom] = dom_idx
    return idx


def build_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
    )


def prepare_story_text(md_text: str) -> str:
    # Use the raw markdown, but remove sections/tags likely to mislead
    t = strip_md_sections(md_text)
    t = strip_html(t)
    # Collapse whitespace
    t = re.sub(r"\s+", " ", t).strip()
    # Guard: eliminate "availability of ..." (resource availability) phrase
    t = re.sub(r"\bavailability of\b[\s\S]*?(?:\.|;|,)", " ", t, flags=re.IGNORECASE)
    return t


def find_best_matches(
    story_text: str,
    labels: List[NFRLabel],
    vectorizer: TfidfVectorizer,
    per_domain: bool,
    threshold: float,
    top_k: int,
) -> List[Tuple[str, str, float]]:
    # Fit vectorizer on labels + story for consistent space
    corpus = [lbl.text for lbl in labels] + [story_text]
    X = vectorizer.fit_transform(corpus)
    label_vecs = X[:-1]
    story_vec = X[-1]
    sims = cosine_similarity(story_vec, label_vecs).ravel()

    # Collect scored labels
    candidates: List[Tuple[str, str, float]] = []
    for i, lbl in enumerate(labels):
        score = float(sims[i])
        if score >= threshold:
            candidates.append((lbl.domain, lbl.code, score))

    if not per_domain:
        # Return top_k overall
        return sorted(candidates, key=lambda x: x[2], reverse=True)[:top_k]

    # Keep top per domain
    best_per_dom: Dict[str, Tuple[str, str, float]] = {}
    for dom, code, score in candidates:
        cur = best_per_dom.get(dom)
        if cur is None or score > cur[2]:
            best_per_dom[dom] = (dom, code, score)
    # Return up to top_k across domains
    return sorted(best_per_dom.values(), key=lambda x: x[2], reverse=True)[:top_k]


def main() -> None:
    ap = argparse.ArgumentParser(description="Semantic Jira→NFR mapper (TF-IDF)")
    ap.add_argument("--keys", help="Comma-separated Jira keys to process (e.g., FTRS-1,FTRS-1600)")
    ap.add_argument("--write", action="store_true", help="Write updates to NFR YAMLs")
    ap.add_argument("--threshold", type=float, default=0.25, help="Cosine similarity threshold [0-1]")
    ap.add_argument("--top", type=int, default=3, help="Top-N matches to consider")
    ap.add_argument("--per-domain", action="store_true", help="Return top match per domain (up to --top)")
    ap.add_argument("--csv", action="store_true", help="Emit CSV: key,domain,code,score")
    args = ap.parse_args()

    labels, domain_data, domain_files = collect_nfr_labels()
    nfr_index = index_nfrs(domain_data)
    vectorizer = build_vectorizer()

    if args.keys:
        keys = [k.strip().upper() for k in args.keys.split(",") if k.strip()]
    else:
        keys = [m.stem.upper() for m in sorted(BACKLOG_DIR.glob("FTRS-*.md"))]

    updated: Dict[str, List[str]] = {}

    for key in keys:
        md_file = BACKLOG_DIR / f"{key}.md"
        if not md_file.exists():
            print(f"Skip {key}: no cache file {md_file}")
            continue
        raw = read_text(md_file)
        story_text = prepare_story_text(raw)
        matches = find_best_matches(
            story_text=story_text,
            labels=labels,
            vectorizer=vectorizer,
            per_domain=args.per_domain,
            threshold=args.threshold,
            top_k=args.top,
        )

        if args.csv:
            for dom, code, score in matches:
                print(f"{key},{dom},{code},{score:.6f}")
        else:
            print(f"\n{key} – top matches (threshold={args.threshold}):")
            for dom, code, score in matches:
                print(f"  {dom}:{code} -> {score:.3f}")

        if args.write:
            for dom, code, score in matches:
                nfr = nfr_index.get(dom, {}).get(code)
                if not nfr:
                    continue
                if ensure_story(nfr, key):
                    updated.setdefault(f"{dom}:{code}", []).append(key)

    if args.write:
        for dom, path in domain_files.items():
            dump_yaml(path, domain_data[dom])
        for bucket, keys in sorted(updated.items()):
            uniq = sorted(set(keys))
            print(f"Updated {bucket}: +{len(uniq)}")


if __name__ == "__main__":
    main()
