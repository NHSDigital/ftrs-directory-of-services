#!/usr/bin/env python3
"""Generate user stories for NFRs that have no stories in domain nfrs.yaml.

- Scans requirements/nfrs/*/nfrs.yaml
- For each NFR with empty `stories`, create a story in requirements/user-stories/backlog/
- Uses a concise template referencing the NFR code and first control metadata if present.
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
DOMAINS_DIR = ROOT / "requirements" / "nfrs"
BACKLOG_DIR = ROOT / "requirements" / "user-stories" / "backlog"
BACKLOG_DIR.mkdir(parents=True, exist_ok=True)

DOMAIN_PREFIXES = {
    "performance": "PERF",
    "security": "SEC",
    "reliability": "REL",
    "observability": "OBS",
    "scalability": "SCAL",
    "accessibility": "ACC",
    "governance": "GOV",
    "interoperability": "INT",
    "cost": "COST",
    "availability": "AVAIL",
    "compatibility": "COMP",
}

ROLE_BY_DOMAIN = {
    "performance": "API Consumer",
    "security": "Security Engineer",
    "reliability": "SRE",
    "observability": "SRE",
    "scalability": "Platform Engineer",
    "accessibility": "UX Engineer",
    "governance": "Governance Lead",
    "interoperability": "Integration Engineer",
    "cost": "FinOps Engineer",
    "availability": "SRE",
    "compatibility": "QA Engineer",
}

TEMPLATE = """---
story_id: {story_id}
title: {title}
role: {role}
goal: {goal}
value: {value}
nfr_refs: [{nfr_code}]
status: draft
---

## Description
{description}

## Acceptance Criteria
- {acceptance_1}
- {acceptance_2}
- {acceptance_3}

## Non-Functional Acceptance
- NFR Code: `{nfr_code}`
- Domain: {domain}
{control_block}

## Traceability
- Domain registry: requirements/nfrs/{domain}/nfrs.yaml
"""


def next_increment(prefix: str) -> int:
    """Find the next STORY-<PREFIX>-NNN increment in backlog files."""
    max_inc = 0
    for p in BACKLOG_DIR.glob(f"STORY-{prefix}-*-*.md"):
        # pattern STORY-<PREFIX>-NNN-...
        name = p.name
        parts = name.split('-')
        if len(parts) >= 3 and parts[1] == prefix:
            try:
                inc = int(parts[2])
                max_inc = max(max_inc, inc)
            except ValueError:
                continue
    return max_inc + 1


def main() -> int:
    created = 0
    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir():
            continue
        nfrs_yaml = domain_dir / "nfrs.yaml"
        if not nfrs_yaml.exists():
            continue
        try:
            data = yaml.safe_load(nfrs_yaml.read_text(encoding="utf-8")) or {}
        except Exception as e:
            sys.stderr.write(f"Failed to read {nfrs_yaml}: {e}\n")
            continue
        domain = domain_dir.name
        prefix = DOMAIN_PREFIXES.get(domain, domain.upper())
        role = ROLE_BY_DOMAIN.get(domain, "Engineer")
        inc = next_increment(prefix)
        for nfr in data.get("nfrs", []) or []:
            stories = nfr.get("stories") or []
            if stories:
                continue
            code = nfr.get("code", "")
            requirement = nfr.get("requirement", "")
            explanation = nfr.get("explanation", "")
            controls = nfr.get("controls", []) or []
            ctrl = controls[0] if controls else {}
            control_block = ""
            if ctrl:
                control_block = (
                    f"- Control ID: `{ctrl.get('control_id','')}`\n"
                    f"- Measure: {ctrl.get('measure','')}\n"
                    f"- Threshold: {ctrl.get('threshold','')}\n"
                    f"- Tooling: {ctrl.get('tooling','')}\n"
                    f"- Cadence: {ctrl.get('cadence','')}\n"
                    f"- Environments: {', '.join(ctrl.get('environments', [])) if isinstance(ctrl.get('environments', []), list) else ctrl.get('environments','')}\n"
                )
            story_id = f"STORY-{prefix}-{inc:03d}"
            title = requirement[:80] or f"{domain} {code}"
            goal = f"Deliver: {requirement}" if requirement else f"Deliver NFR {code}"
            value = explanation or requirement or f"Satisfy non-functional requirement {code}"
            description = f"Implement and validate NFR `{code}` for domain `{domain}`."
            acceptance_1 = ctrl.get('threshold','Define measurable threshold') if ctrl else "Define measurable threshold"
            acceptance_2 = "Tooling and cadence established"
            acceptance_3 = "Monitoring and alerting in place"
            content = TEMPLATE.format(
                story_id=story_id,
                title=title,
                role=role,
                goal=goal,
                value=value,
                nfr_code=code,
                domain=domain,
                description=description,
                acceptance_1=acceptance_1,
                acceptance_2=acceptance_2,
                acceptance_3=acceptance_3,
                control_block=control_block,
            )
            fname_slug = (ctrl.get('control_id','nfr') if ctrl else code).lower()
            out = BACKLOG_DIR / f"{story_id}-{fname_slug}.md"
            out.write_text(content, encoding="utf-8")
            created += 1
            inc += 1
            print(f"Created {out}")
    if created:
        print(f"Generated {created} user stories for NFRs without stories.")
    else:
        print("No NFRs without stories found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
