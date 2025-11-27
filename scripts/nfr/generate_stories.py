#!/usr/bin/env python3
import yaml
from pathlib import Path

REQUIREMENTS_DIR = Path("requirements")
NFRS_DIR = REQUIREMENTS_DIR / "nfrs"
STORIES_DIR = REQUIREMENTS_DIR / "user-stories" / "backlog"

STORY_TEMPLATE = """---
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
{acceptance_criteria}

## Non-Functional Acceptance
{nfr_acceptance}

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

## Out of Scope
Implementation details to be refined during sprint planning

## Implementation Notes
{implementation_notes}

## Monitoring & Metrics
{metrics}

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Configuration drift | Non-compliance | Automated remediation |
| Tool failures | Missed violations | Redundant checks |

## Traceability
- NFR: {nfr_code}
- Registry: {registry_path}

## Open Questions
None
"""

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
    "compatibility": "COMP"
}

DOMAIN_ROLES = {
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
    "compatibility": "QA Engineer"
}

def generate_performance_stories(data, start_num=1):
    """Generate performance stories from operations"""
    operations = data.get('operations', [])
    story_num = start_num

    for op in operations:
        operation_id = op['operation_id']
        service = op['service']
        story_id = f"STORY-PERF-{story_num:03d}"

        # Build acceptance criteria for performance
        ac_lines = [
            f"1. p50 latency ≤{op['p50_target_ms']}ms validated",
            f"2. p95 latency ≤{op['p95_target_ms']}ms validated",
            f"3. Absolute max latency ≤{op.get('absolute_max_ms', 'N/A')}ms enforced",
            f"4. Load testing completed successfully"
        ]

        # Add throughput criteria if present
        if 'burst_tps_target' in op:
            ac_lines.append(f"5. Burst throughput: {op['burst_tps_target']} TPS sustained")
            ac_lines.append(f"6. Sustained throughput: {op['sustained_tps_target']} TPS maintained")

        impl_notes = [
            f"- {op['rationale']}",
            f"- Service: {service}",
            f"- Path: {op.get('path', 'N/A')}",
            f"- Method: {op.get('method', 'N/A')}",
            f"- Concurrency profile: {op.get('concurrency_profile', 'N/A')}",
            f"- Status: {op.get('status', 'draft')}"
        ]

        metrics = [
            f"- `{operation_id.replace('-', '_')}_latency_ms` histogram (p50, p95, p99)",
            f"- `{operation_id.replace('-', '_')}_requests_total` counter",
            f"- `{operation_id.replace('-', '_')}_errors_total` counter"
        ]

        if 'burst_tps_target' in op:
            metrics.append(f"- `{operation_id.replace('-', '_')}_tps` gauge")

        story_content = STORY_TEMPLATE.format(
            story_id=story_id,
            title=f"{service} {operation_id} Performance",
            role="API Consumer",
            goal=f"Receive response from {operation_id} within performance targets",
            value=op['rationale'],
            nfr_code="PERF-001",
            description=f"Implement and validate performance for {service} operation: {operation_id}.",
            acceptance_criteria='\n'.join(ac_lines),
            nfr_acceptance=f"- Operation ID: `{operation_id}`\\n- Service: {service}\\n- p50: ≤{op['p50_target_ms']}ms\\n- p95: ≤{op['p95_target_ms']}ms\\n- Max: ≤{op.get('absolute_max_ms', 'N/A')}ms",
            implementation_notes='\n'.join(impl_notes),
            metrics='\n'.join(metrics),
            registry_path=f"performance/expectations.yaml v{data.get('version', '1.0')}"
        )

        filename = STORIES_DIR / f"{story_id}-{operation_id}.md"
        with open(filename, 'w') as f:
            f.write(story_content)

        print(f"Created {story_id}")
        story_num += 1

    return story_num

def generate_domain_stories(domain, start_num=1):
    registry_file = NFRS_DIR / domain / "expectations.yaml"
    if not registry_file.exists():
        print(f"Skipping {domain}")
        return start_num

    with open(registry_file) as f:
        data = yaml.safe_load(f)

    # Performance has 'operations' instead of 'controls'
    if domain == "performance":
        return generate_performance_stories(data, start_num)

    controls = data.get('controls', [])
    domain_prefix = DOMAIN_PREFIXES[domain]
    role = DOMAIN_ROLES[domain]

    story_num = start_num
    for control in controls:
        control_id = control['control_id']
        nfr_code = control['nfr_code']
        story_id = f"STORY-{domain_prefix}-{story_num:03d}"

        ac_lines = [
            f"1. {control['threshold']}",
            f"2. Tooling: {control['tooling']} operational",
            f"3. Cadence: {control['cadence']} validated",
            f"4. Environments: {', '.join(control['environments'])} covered",
            f"5. Monitoring configured and alerting tested"
        ]

        impl_notes = [
            f"- {control['rationale']}",
            f"- Cadence: {control['cadence']}",
            f"- Status: {control['status']}"
        ]

        metric_prefix = control_id.replace('-', '_')
        metrics = [
            f"- `{metric_prefix}_compliance_status` gauge",
            f"- `{metric_prefix}_violations_total` counter"
        ]

        story_content = STORY_TEMPLATE.format(
            story_id=story_id,
            title=control['measure'][:80],
            role=role,
            goal=f"Implement and validate: {control['measure']}",
            value=control['rationale'],
            nfr_code=nfr_code,
            description=f"Implement automated validation for: {control['measure']}.",
            acceptance_criteria='\n'.join(ac_lines),
            nfr_acceptance=f"- Control ID: `{control_id}`\\n- Threshold: {control['threshold']}\\n- Tooling: {control['tooling']}\\n- Cadence: {control['cadence']}\\n- Environments: {', '.join(control['environments'])}",
            implementation_notes='\n'.join(impl_notes),
            metrics='\n'.join(metrics),
            registry_path=f"{domain}/expectations.yaml v{data.get('version', '1.0')}"
        )

        filename = STORIES_DIR / f"{story_id}-{control_id}.md"
        with open(filename, 'w') as f:
            f.write(story_content)

        print(f"Created {story_id}")
        story_num += 1

    return story_num

if __name__ == "__main__":
    # Generate all domains from 1
    for domain in ["performance", "security", "reliability", "observability", "scalability", "accessibility", "governance", "interoperability", "cost", "availability", "compatibility"]:
        next_num = generate_domain_stories(domain, 1)
        print(f"{domain.capitalize()}: {next_num - 1} stories")
