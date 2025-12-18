#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
from typing import Dict, Any

try:
    import yaml  # type: ignore
except Exception as e:
    print("Missing PyYAML. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
DOMAINS_DIR = ROOT / "requirements" / "nfrs"
EXPL_PATH = ROOT / "requirements" / "nfrs" / "cross-references" / "nfr-explanations.yaml"


def load_code_domains() -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for d in DOMAINS_DIR.iterdir():
        if not d.is_dir():
            continue
        f = d / "nfrs.yaml"
        if not f.exists():
            continue
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        for n in data.get("nfrs", []) or []:
            code = str(n.get("code", "")).strip()
            if code:
                mapping[code] = d.name.capitalize()
    return mapping


SECURITY_WHY_OVERRIDES: Dict[str, list[str]] = {
    "SEC-001": [
        "Weak algorithms are routinely broken; approved crypto preserves confidentiality and integrity.",
        "Avoids interoperability and compliance issues from deprecated cipher use.",
    ],
    "SEC-003": [
        "Encrypting data in transit prevents interception and tampering over networks.",
        "Meets baseline security expectations and external assurance requirements.",
    ],
    "SEC-004": [
        "Encryption at rest mitigates impact of storage compromise or media loss.",
        "Enables key revocation and granular access control via KMS.",
    ],
    "SEC-005": [
        "Environment isolation prevents accidental cross-environment data access.",
        "Reduces blast radius of faults and credentials leakage.",
    ],
    "SEC-006": [
        "Unrestricted console access creates untracked changes and insider risk.",
        "Break‑glass ensures urgent fixes remain auditable and time‑bounded.",
    ],
    "SEC-007": [
        "Broad ingress rules expose unnecessary attack surface.",
        "Principle of least privilege applies to network pathways.",
    ],
    "SEC-009": [
        "Standards‑based scans detect common misconfigurations early.",
        "Continuous hygiene avoids drift and audit findings.",
    ],
    "SEC-010": [
        "Independent testing finds real‑world exploit chains beyond automated scans.",
        "Prioritises remediation by demonstrated impact.",
    ],
    "SEC-011": [
        "Security must not silently degrade performance SLAs.",
        "Prevents teams from bypassing controls due to latency pain.",
    ],
    "SEC-012": [
        "Least privilege reduces lateral movement and blast radius.",
        "Role reviews remove accumulated permissions over time.",
    ],
    "SEC-013": [
        "Key rotation limits exposure from key disclosure.",
        "Operationalises crypto hygiene across systems.",
    ],
    "SEC-014": [
        "mTLS authenticates both peers and protects sensitive internal flows.",
        "Prevents credential replay and man‑in‑the‑middle attacks.",
    ],
    "SEC-015": [
        "Expired certificates cause outages and trust failures.",
        "Early detection enables safe, no‑downtime renewals.",
    ],
    "SEC-016": [
        "MFA reduces compromise risk of privileged accounts.",
        "Meets NHS security expectations for admin access.",
    ],
    "SEC-017": [
        "Long‑lived secrets leak and are hard to rotate.",
        "Scanning enforces managed, short‑lived credentials only.",
    ],
    "SEC-018": [
        "Third‑party weaknesses can become your incident.",
        "Supplier assurance evidences baseline security posture.",
    ],
    "SEC-019": [
        "Segmentation prevents cross‑tenant data exposure.",
        "Regular tests validate isolation controls remain effective.",
    ],
    "SEC-020": [
        "Trusting only valid certificates prevents spoofing.",
        "Certificate hygiene underpins secure connections.",
    ],
    "SEC-021": [
        "Unexpected ports indicate misconfiguration or backdoors.",
        "Routine scans reduce exposure window.",
    ],
    "SEC-022": [
        "Powerful utilities enable privilege escalation and data exfiltration.",
        "Restricting access reduces misuse risk.",
    ],
    "SEC-023": [
        "Shared pipeline identities hide accountability.",
        "Per‑stage identities create a clear provenance trail.",
    ],
    "SEC-024": [
        "Integrity checks prevent silent corruption or tampering in transit.",
        "Secure channels protect confidentiality end‑to‑end.",
    ],
    "SEC-025": [
        "PID in transit demands the strongest transport protections (mTLS).",
        "Prevents interception of identifiable patient data.",
    ],
    "SEC-026": [
        "Avoiding PID in responses reduces data handling obligations.",
        "Minimises breach impact surface.",
    ],
    "SEC-027": [
        "Critical CVEs in dependencies are a common breach vector.",
        "Fail‑fast gating enforces timely patching.",
    ],
    "SEC-028": [
        "Releasing with known critical findings creates unacceptable risk.",
        "Blocking ensures risk is consciously owned or remediated.",
    ],
    "SEC-029": [
        "Strong auth reduces fraud and misuse of clinical systems.",
        "Validating all JWT claims prevents token confusion and downgrade attacks.",
    ],
    "SEC-030": [
        "Plaintext secrets in repos or images are easily exfiltrated.",
        "Approved secret stores enforce encryption, rotation, and access controls.",
    ],
}


def domain_boilerplate(domain: str, code: str) -> Dict[str, str]:
    dom = domain.lower()
    bp = {
        "why": [
            "Clarifies intent and outcomes for this NFR so teams know what good looks like.",
            "Helps align implementation and evidence across services consistently.",
        ],
        "accept": [
            f"Controls for {code} appear on service pages with status, measure, threshold, cadence, and rationale.",
            "Evidence is linked or attached (dashboards, scans, minutes, tickets) and reviewed per cadence.",
        ],
        "except": [
            "Only by prior approval with stakeholder sign‑off; include mitigation and expiry date.",
        ],
    }
    if dom == "security":
        bp["why"] = SECURITY_WHY_OVERRIDES.get(code, [
            "Reduces risk of data breach and unauthorized access.",
            "Meets NHS and statutory security obligations with auditable evidence.",
        ])
        bp["accept"][1] = "Security tooling outputs (e.g., ASVS/CIS scans, SIEM alerts, pen test reports) are retained."
    elif dom == "performance":
        bp["why"] = [
            "Protects user experience and prevents capacity regressions.",
            "Ensures predictable latency and throughput under typical and peak load.",
        ]
        bp["accept"][1] = "Performance test results and targets (p50/p95/TPS/payload) are recorded and monitored."
    elif dom == "reliability":
        bp["why"] = [
            "Improves service continuity during faults and failures.",
            "Supports recovery objectives with tested resilience patterns.",
        ]
        bp["accept"][1] = "Failover drills and runbooks demonstrate RPO/RTO and graceful degradation."
    elif dom == "observability":
        bp["why"] = [
            "Enables fast detection, triage, and resolution of incidents.",
            "Provides actionable telemetry for product and reliability decisions.",
        ]
        bp["accept"][1] = "Dashboards, logs, traces, and alerts exist with freshness and coverage targets."
    elif dom == "availability":
        bp["why"] = [
            "Maintains user trust with predictable uptime and planned maintenance windows.",
            "Ensures DR objectives can be achieved during regional or AZ faults.",
        ]
        bp["accept"][1] = "Uptime SLOs, DR tests, and maintenance records are documented and reviewed."
    elif dom == "scalability":
        bp["why"] = [
            "Supports growth without performance degradation or disproportionate cost.",
            "Keeps scaling actions safe, observable, and reversible.",
        ]
        bp["accept"][1] = "Autoscaling and capacity plans are tested; scale events are auditable."
    elif dom == "interoperability":
        bp["why"] = [
            "Reduces integration friction for consuming systems and partners.",
            "Preserves semantics and compatibility across versions.",
        ]
        bp["accept"][1] = "Contracts, validators, and changelogs exist; compatibility tests run in CI."
    elif dom == "accessibility":
        bp["why"] = [
            "Meets legal requirements and ensures inclusive user experience.",
            "Prevents regressions through automation and manual audits.",
        ]
        bp["accept"][1] = "WCAG audits and CI scans pass with tracked remediation."
    elif dom == "cost":
        bp["why"] = [
            "Controls cloud spend and avoids waste while meeting SLAs.",
            "Enables clear ownership and accountability via tagging and reports.",
        ]
        bp["accept"][1] = "Budgets, alerts, and reviews exist; actions tracked with owners."
    elif dom == "governance":
        bp["why"] = [
            "Demonstrates due diligence and alignment with NHS governance.",
            "Provides audit-ready evidence for approvals and compliance.",
        ]
        bp["accept"][1] = "Approvals, minutes, and checklists stored with clear links and statuses."
    elif dom == "compatibility":
        bp["why"] = [
            "Prevents user experience issues across supported platforms.",
            "Reduces support costs and avoids integration surprises.",
        ]
        bp["accept"][1] = "Version/OS/browser matrices and test results are maintained."
    return bp


def is_multiline(text: str) -> bool:
    return isinstance(text, str) and ("\n" in text or text.strip().endswith(":"))


def ensure_block(summary: str, domain: str, code: str) -> str:
    bp = domain_boilerplate(domain, code)
    lines = []
    lines.append(str(summary).strip())
    lines.append("")
    lines.append("Why this matters:")
    # Add a code-specific first bullet derived from the summary for specificity
    summ = str(summary).strip().rstrip('.')
    if summ:
        lines.append(f"- Ensures {summ}.")
    for w in bp["why"]:
        lines.append(f"- {w}")
    lines.append("")
    lines.append("Acceptance (evidence we expect to see):")
    for a in bp["accept"]:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("Exceptions:")
    for e in bp["except"]:
        lines.append(f"- {e}")
    return "\n".join(lines)


def _first_paragraph(text: str) -> str:
    if not isinstance(text, str):
        return ""
    parts = text.split("\n\n", 1)
    return parts[0].strip()


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild-domain", action="append", default=[], help="Force rebuild of boilerplate for a domain (e.g., security)")
    ap.add_argument("--rebuild-codes", default="", help="Comma-separated codes to force rebuild")
    args = ap.parse_args()

    code_domains = load_code_domains()
    data: Dict[str, Any] = yaml.safe_load(EXPL_PATH.read_text(encoding="utf-8")) or {}
    explanations: Dict[str, Any] = data.get("explanations") or {}
    changed = 0
    force_codes = {c.strip().upper() for c in (args.rebuild_codes.split(",") if args.rebuild_codes else []) if c.strip()}
    force_domains = {d.strip().lower() for d in args.rebuild_domain}
    for code, text in list(explanations.items()):
        dom = code_domains.get(code, "")
        if not dom:
            continue
        must_force = (code in force_codes) or (dom.lower() in force_domains)
        if isinstance(text, str):
            if not is_multiline(text):
                # single-line -> enrich
                explanations[code] = ensure_block(text, dom, code)
                changed += 1
            elif must_force:
                # preserve the first paragraph as summary; rebuild the sections
                summary = _first_paragraph(text)
                explanations[code] = ensure_block(summary, dom, code)
                changed += 1
    if changed:
        data["explanations"] = explanations
        EXPL_PATH.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
        print(f"Updated explanations for {changed} codes.")
    else:
        print("No single-line explanations found to enrich.")


if __name__ == "__main__":
    main()
