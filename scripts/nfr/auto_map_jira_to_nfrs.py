#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

import yaml

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


def ensure_story(nfr: Dict[str, Any], key: str) -> bool:
    stories = nfr.get("stories")
    if stories is None:
        nfr["stories"] = [key]
        return True
    if key not in stories:
        stories.append(key)
        return True
    return False


def classify_and_targets(text: str) -> List[Tuple[str, str]]:
    t = text.lower()
    matches: List[Tuple[str, str]] = []

    def hit(words: List[str]) -> bool:
        return any(w.lower() in t for w in words)

    # Security mappings
    if hit(["jwt", "cis2", "openid", "oidc", "token"]):
        matches.append(("security", "SEC-029"))
    if hit(["mtls", "mutual tls", "client certificate", "certificate chain", "ocsp", "revocation", "intermediate ca"]):
        matches.append(("security", "SEC-014"))
    if hit(["expiry", "expire", "renewal", "renew", "rotate", "rotation"]) and hit(["cert", "certificate"]):
        matches.append(("security", "SEC-015"))
    if hit(["secret", "secrets manager", "kms", "plaintext", "hardcoded", "key rotation"]):
        matches.append(("security", "SEC-030"))
    if hit(["waf", "rate-based", "bot", "ddos"]):
        matches.append(("security", "SEC-002"))
    if hit(["cve", "vulnerab", "dependency", "container", "trivy", "inspector"]):
        matches.append(("security", "SEC-027"))
    if hit(["iam", "least privilege", "policy"]):
        matches.append(("security", "SEC-012"))
    if hit(["port scan"]):
        matches.append(("security", "SEC-021"))

    # Observability mappings
    if hit(["_ping", "_status", "health", "healthcheck", "monitoring endpoint"]):
        matches.append(("observability", "OBS-001"))
    if hit(["tps", "throughput"]):
        matches.append(("observability", "OBS-008"))
    if hit(["histogram", "p50", "p95", "p99"]):
        matches.append(("observability", "OBS-009"))
    if hit(["error percentage", "error%", "error rate"]) or hit(["alert"]) and hit(["error"]):
        matches.append(("observability", "OBS-012"))
    if hit(["4xx", "5xx", "per-endpoint"]):
        matches.append(("observability", "OBS-032"))
    if hit(["unauthorized", "forbidden", "rate limit breach", "failed auth", "credential stuffing"]):
        matches.append(("observability", "OBS-033"))
    if hit(["trace", "x-ray", "distributed trace"]):
        matches.append(("observability", "OBS-030"))

    # Availability mappings
    if hit(["dr", "disaster", "ransomware", "recover to new account"]):
        matches.append(("availability", "AVAIL-002"))
        matches.append(("availability", "AVAIL-006"))
    if hit(["uptime", "availability", "sla", "slo"]):
        matches.append(("availability", "AVAIL-001"))
    if hit(["blue/green", "blue green"]):
        matches.append(("availability", "AVAIL-010"))

    # Reliability mappings
    if hit(["ddos", "dos", "attack"]):
        matches.append(("reliability", "REL-004"))
    if hit(["fault injection", "fis", "tier failure", "graceful degradation"]):
        matches.append(("reliability", "REL-013"))
    if hit(["restore drill", "backup", "aws backup", "ransomware"]):
        matches.append(("reliability", "REL-017"))

    # Performance mappings
    if hit(["burst", "spike"]):
        matches.append(("performance", "PERF-011"))
    if hit(["sustained", "steady", "rate limit", "tps", "throughput"]):
        matches.append(("performance", "PERF-012"))
    if hit(["latency", "response time", "performance test", "jmeter", "neoload", "p95", "p50"]):
        matches.append(("performance", "PERF-001"))
    if hit(["payload", "request size", "1mb", "payload limit"]):
        matches.append(("performance", "PERF-013"))

    # Accessibility
    if hit(["accessibility", "wcag"]):
        matches.append(("accessibility", None))  # do not assign specific code here

    return matches


def build_domain_files() -> Dict[str, Path]:
    domain_files: Dict[str, Path] = {}
    for domain_dir in NFRS_ROOT.iterdir():
        if domain_dir.is_dir():
            f = domain_dir / "nfrs.yaml"
            if f.exists():
                domain_files[domain_dir.name] = f
    return domain_files


def index_nfrs(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    idx: Dict[str, Dict[str, Any]] = {}
    for nfr in data.get("nfrs", []):
        code = nfr.get("code")
        if code:
            idx[code] = nfr
    return idx


def main() -> None:
    domain_files = build_domain_files()
    # Load all domain YAMLs
    domain_data: Dict[str, Dict[str, Any]] = {dom: load_yaml(path) for dom, path in domain_files.items()}
    domain_indexes: Dict[str, Dict[str, Dict[str, Any]]] = {dom: index_nfrs(data) for dom, data in domain_data.items()}

    # Scan backlog Jira files
    md_files = sorted(BACKLOG_DIR.glob("FTRS-*.md"))
    added: Dict[str, List[str]] = {}

    for md in md_files:
        text = read_text(md)
        key_match = re.search(r"FTRS-\d+", md.name)
        if not key_match:
            continue
        key = key_match.group(0)
        targets = classify_and_targets(text)
        for domain, nfr_code in targets:
            if domain not in domain_data:
                continue
            if nfr_code is None:
                # skip specific code mapping for accessibility
                continue
            nfr = domain_indexes[domain].get(nfr_code)
            if not nfr:
                continue
            if ensure_story(nfr, key):
                added.setdefault(f"{domain}:{nfr_code}", []).append(key)

    # Write back
    for dom, path in domain_files.items():
        dump_yaml(path, domain_data[dom])

    # Report summary
    for bucket, keys in sorted(added.items()):
        uniq = sorted(set(keys))
        print(f"Updated {bucket}: +{len(uniq)}")


if __name__ == "__main__":
    main()
