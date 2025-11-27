#!/usr/bin/env python3
"""Generate a simplified aggregated NFR page for Confluence copy/paste.

Reads the NFR cross reference matrix (requirements/nfrs/cross-references/nfr-matrix.md)
and produces docs/developer-guides/nfr-all-simplified.md with per-domain sections.

Simplification rules:
 - Use table rows from the matrix.
 - For each row, treat the "Acceptance Criteria Anchor" column as the short requirement line.
 - Group by Domain.
 - Sort codes within a domain numerically (by the number after the prefix).
 - Include related story IDs comma-separated.

Idempotent: running again overwrites the file.
"""
from __future__ import annotations
from pathlib import Path
import re
from datetime import datetime, timezone
import yaml
import json

BACKLOG_DIR = Path("requirements/user-stories/backlog")

MATRIX = Path("requirements/nfrs/cross-references/nfr-matrix.md")
OUT = Path("docs/developer-guides/nfr-all-simplified.md")
# New: domain-specific output directory for split pages
DOMAIN_OUT_DIR = Path("docs/developer-guides/nfr-domains")
EXPECTATIONS = Path("requirements/nfrs/performance/expectations.yaml")
SEC_EXPECTATIONS = Path("requirements/nfrs/security/expectations.yaml")
OBS_EXPECTATIONS = Path("requirements/nfrs/observability/expectations.yaml")
REL_EXPECTATIONS = Path("requirements/nfrs/reliability/expectations.yaml")
AVAIL_EXPECTATIONS = Path("requirements/nfrs/availability/expectations.yaml")
SCAL_EXPECTATIONS = Path("requirements/nfrs/scalability/expectations.yaml")
INT_EXPECTATIONS = Path("requirements/nfrs/interoperability/expectations.yaml")
ACC_EXPECTATIONS = Path("requirements/nfrs/accessibility/expectations.yaml")
COST_EXPECTATIONS = Path("requirements/nfrs/cost/expectations.yaml")
GOV_EXPECTATIONS = Path("requirements/nfrs/governance/expectations.yaml")
COMP_EXPECTATIONS = Path("requirements/nfrs/compatibility/expectations.yaml")

ROW_PATTERN = re.compile(r"^\|\s*([A-Z]+-[0-9]+)\s*\|\s*([A-Za-z]+)\s*\|\s*([^|]*)\|\s*([^|]*)\|")
EXPLANATIONS_FILE = Path("requirements/nfrs/cross-references/nfr-explanations.yaml")

def parse_rows(text: str):
    rows = []
    for line in text.splitlines():
        m = ROW_PATTERN.match(line)
        if not m:
            continue
        code, domain, stories, anchor = [x.strip() for x in m.groups()]
        # Normalize empty stories
        stories = stories if stories else "(none)"
        rows.append({"code": code, "domain": domain, "stories": stories, "anchor": anchor})
    return rows

def sort_key(row):
    prefix, num = row["code"].split("-")
    try:
        return (prefix, int(num))
    except ValueError:
        return (prefix, num)

def load_expectations():
    if not EXPECTATIONS.exists():
        return None
    data = yaml.safe_load(EXPECTATIONS.read_text(encoding="utf-8"))
    ops = data.get("operations", [])
    # group by service
    by_service = {}
    for op in ops:
        by_service.setdefault(op.get("service", "unknown"), []).append(op)
    # sort operations per service by operation_id
    for svc_ops in by_service.values():
        svc_ops.sort(key=lambda o: o.get("operation_id", ""))
    return {"version": data.get("version"), "generated": data.get("generated"), "by_service": by_service}

def load_security_expectations():
    if not SEC_EXPECTATIONS.exists():
        return None
    data = yaml.safe_load(SEC_EXPECTATIONS.read_text(encoding="utf-8"))
    items = data.get("controls", [])
    # sort by nfr_code then control_id
    items.sort(key=lambda c: (c.get("nfr_code", ""), c.get("control_id", "")))
    return {"version": data.get("version"), "generated": data.get("generated"), "items": items}

def load_controls_registry(path: Path):
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    items = data.get("controls", [])
    items.sort(key=lambda c: (c.get("nfr_code", ""), c.get("control_id", "")))
    return {"version": data.get("version"), "generated": data.get("generated"), "items": items}

def render_controls_section(lines: list[str], title: str, reg: dict):
    lines.append(f"## {title}")
    lines.append("")
    lines.append(f"Version: {reg['version']} Generated: {reg['generated']}")
    lines.append("")
    lines.append("Below is a quick guide to the table columns:")
    lines.append("")
    lines.append("- Control ID: Stable identifier for a governance control or check")
    lines.append("- NFR Code: Mapped domain NFR (e.g., OBS-005, REL-010)")
    lines.append("- Measure: What is being verified (policy/setting/behaviour)")
    lines.append("- Threshold: Quantified acceptance (e.g., 100% compliant, <= threshold)")
    lines.append("- Tooling: Primary automation/tool used to verify the measure")
    lines.append("- Cadence: How often the check runs (CI per build, daily, continuous)")
    lines.append("- Envs: Environments covered (dev/int/ref/prod)")
    lines.append("- Services: Targeted services if not universal (comma-separated); blank implies all")
    lines.append("- Status: Governance state (draft, accepted, exception)")
    lines.append("- Rationale: Why this threshold/tooling was chosen; notes/assumptions")
    lines.append("")
    lines.append("| Control ID | NFR Code | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |")
    lines.append("|------------|----------|---------|-----------|---------|---------|------|----------|--------|-----------|")
    for c in reg["items"]:
        ctrl = c.get("control_id", "")
        nfr = c.get("nfr_code", "")
        measure = c.get("measure", "").replace("|","/")
        threshold = c.get("threshold", "").replace("|","/")
        tooling = c.get("tooling", "")
        cadence = c.get("cadence", "")
        envs = ",".join(c.get("environments", [])) if isinstance(c.get("environments"), list) else c.get("environments", "")
        services = ",".join(c.get("services", [])) if isinstance(c.get("services"), list) else c.get("services", "")
        status = c.get("status", "")
        rationale = c.get("rationale", "").replace("\n"," ").replace("|","/")
        lines.append(f"| {ctrl} | {nfr} | {measure} | {threshold} | {tooling} | {cadence} | {envs} | {services} | {status} | {rationale} |")
    lines.append("")
    lines.append("(Refer to the domain expectations.yaml for additional metadata including evidence links and exception records.)")
    lines.append("")

def build_domain_pages(by_domain: dict[str, list[dict]], explanations: dict[str,str], registries: dict[str, dict]):
    """Generate per-domain pages for improved readability.

    For each domain:
      - Render NFR table (Code, Requirement, Explanation, Stories)
      - For Performance domain include operations table.
      - For control-centric domains group controls under each NFR code heading.
    """
    DOMAIN_OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Removed volatile per-run timestamp to reduce unnecessary diffs
    story_jira_map = load_story_jira_map()
    for domain, rows in by_domain.items():
        fname = DOMAIN_OUT_DIR / f"{domain.lower()}.md"
        lines: list[str] = [f"# FtRS NFR – {domain}", "", "Source: requirements/nfrs/cross-references/nfr-matrix.md", "", "This page is auto-generated; do not hand-edit.", ""]
        # NFR codes table
        lines.append("## NFR Codes")
        lines.append("")
        lines.append("| Code | Requirement | Explanation | Stories |")
        lines.append("|------|-------------|-------------|---------|")
        for r in rows:
            req = r['anchor'].replace('|','/')
            expl = explanations.get(r['code'], explanations.get('__error__', req)) or req
            expl = expl.replace('|','/').replace('\n',' ')
            stories_raw = r['stories']
            stories_list = [s.strip() for s in stories_raw.split(',') if s.strip() and s.strip() != '(none)']
            enriched: list[str] = []
            for s in stories_list:
                # strip any existing jira parentheses
                base = s.split('(')[0].strip()
                jira = story_jira_map.get(base)
                if jira:
                    enriched.append(f"{base} ({jira})")
                else:
                    enriched.append(base)
            stories_display = ', '.join(enriched) if enriched else '(none)'
            lines.append(f"| {r['code']} | {req} | {expl} | {stories_display} |")
        lines.append("")
        # Domain specific expectations
        if domain.lower() == "performance":
            perf = registries.get("performance")
            if perf:
                lines.append("## Operations")
                lines.append("")
                # Show only stable version; omit generated date to minimise churn
                lines.append(f"Version: {perf['version']}")
                lines.append("")
                lines.append("| Service | Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |")
                lines.append("|---------|--------------|--------|--------|--------|----------|--------------|---------------------|--------|-----------|")
                for svc in sorted(perf['by_service'].keys()):
                    for op in perf['by_service'][svc]:
                        op_id = op.get('operation_id')
                        p50 = op.get('p50_target_ms')
                        p95 = op.get('p95_target_ms')
                        mx = op.get('absolute_max_ms')
                        burst = op.get('burst_tps_target', '')
                        sustained = op.get('sustained_tps_target', '')
                        payload = op.get('max_request_payload_bytes', '')
                        status = op.get('status')
                        rationale = op.get('rationale','').replace('\n',' ').replace('|','/')
                        lines.append(f"| {svc} | {op_id} | {p50} | {p95} | {mx} | {burst} | {sustained} | {payload} | {status} | {rationale} |")
                lines.append("")
        else:
            # control-centric domain
            reg_key = domain.lower()
            registry = registries.get(reg_key)
            if registry:
                # group controls by nfr_code for contextual display
                grouped: dict[str, list[dict]] = {}
                for item in registry['items']:
                    code = item.get('nfr_code', 'UNKNOWN')
                    grouped.setdefault(code, []).append(item)
                lines.append("## Controls")
                lines.append("")
                for code in sorted(grouped.keys()):
                    lines.append(f"### {code}")
                    if code in explanations:
                        lines.append(explanations[code])
                    lines.append("")
                    lines.append("| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |")
                    lines.append("|------------|---------|-----------|---------|---------|------|----------|--------|-----------|")
                    for c in grouped[code]:
                        ctrl = c.get('control_id','')
                        measure = c.get('measure','').replace('|','/').replace('\n',' ')
                        threshold = c.get('threshold','').replace('|','/')
                        tooling = c.get('tooling','')
                        cadence = c.get('cadence','')
                        envs = ",".join(c.get('environments', [])) if isinstance(c.get('environments'), list) else c.get('environments','')
                        services = ",".join(c.get('services', [])) if isinstance(c.get('services'), list) else c.get('services','')
                        status = c.get('status','')
                        rationale = c.get('rationale','').replace('\n',' ').replace('|','/')
                        lines.append(f"| {ctrl} | {measure} | {threshold} | {tooling} | {cadence} | {envs} | {services} | {status} | {rationale} |")
                    lines.append("")
        fname.write_text("\n".join(lines)+"\n", encoding="utf-8")
        print(f"Wrote domain page: {fname}")

def build_output(rows):
    by_domain = {}
    for r in rows:
        by_domain.setdefault(r["domain"], []).append(r)
    for domain_rows in by_domain.values():
        domain_rows.sort(key=sort_key)
    domains_sorted = sorted(by_domain.keys())
    # Omit volatile timestamp to keep commits clean
    lines = ["# FtRS Non-Functional Requirements – Simplified", "", "Source: requirements/nfrs/cross-references/nfr-matrix.md", "", "This page is auto-generated; do not hand-edit. Run `python3 scripts/nfr/refresh_simplified_nfr_page.py` to refresh.", ""]

    explanations = {}
    if EXPLANATIONS_FILE.exists():
        try:
            exp_data = yaml.safe_load(EXPLANATIONS_FILE.read_text(encoding="utf-8")) or {}
            for code, text in (exp_data.get("explanations", {}) or {}).items():
                explanations[code] = text.strip()
        except Exception as e:
            explanations["__error__"] = f"Failed to parse explanations file: {e}"
    # Load registries once for both index summary and domain pages
    expectations = load_expectations()
    sec_expectations = load_security_expectations()
    registries: dict[str, dict] = {}
    if expectations:
        registries['performance'] = expectations
    if sec_expectations:
        registries['security'] = sec_expectations
    reg_map = [
        ('observability', OBS_EXPECTATIONS),
        ('reliability', REL_EXPECTATIONS),
        ('availability', AVAIL_EXPECTATIONS),
        ('scalability', SCAL_EXPECTATIONS),
        ('interoperability', INT_EXPECTATIONS),
        ('accessibility', ACC_EXPECTATIONS),
        ('cost', COST_EXPECTATIONS),
        ('governance', GOV_EXPECTATIONS),
        ('compatibility', COMP_EXPECTATIONS),
    ]
    for name, path in reg_map:
        reg = load_controls_registry(path)
        if reg:
            registries[name] = reg

    # Build domain pages (split files)
    build_domain_pages(by_domain, explanations, registries)
    # Index summary linking to split pages
    lines.append("## Domain Index")
    lines.append("")
    lines.append("| Domain | NFR Codes | Expectations Items | Page |")
    lines.append("|--------|-----------|--------------------|------|")
    for d in domains_sorted:
        code_count = len(by_domain[d])
        reg_key = d.lower()
        reg = registries.get(reg_key)
        item_count = 0
        if reg:
            if reg_key == 'performance':
                # count operations
                item_count = sum(len(v) for v in reg['by_service'].values())
            else:
                item_count = len(reg['items'])
        page_path = f"nfr-domains/{d.lower()}.md"
        lines.append(f"| {d} | {code_count} | {item_count} | [{d}]({page_path}) |")
    lines.append("")

    # Guard: warn if any codes missing explanations (excluding parse error fallback)
    if '__error__' not in explanations:
        codes = [r['code'] for r in rows]
        missing = sorted({c for c in codes if c not in explanations})
        if missing:
            print(f"WARNING: Missing explanations for {len(missing)} NFR codes: {', '.join(missing)}")
            lines.append("### Explanation Coverage Warning")
            lines.append("")
            lines.append(f"The following NFR codes are missing plain-language explanations in `nfr-explanations.yaml`: {', '.join(missing)}")
            lines.append("")

    # Previously full registry tables moved to per-domain pages for readability.
    lines.append("### Notes")
    lines.append("")
    lines.append("Per-domain pages now contain detailed operations or controls grouped by NFR code. This index intentionally omits those large tables for comprehension.")
    lines.append("")
    # Add explanatory sections (auto-generated) for performance operations and controls
    # Choose an example performance operation (prefer org-search-ods, else first)
    example_op = None
    perf_reg = registries.get('performance')
    if perf_reg:
        for svc in sorted(perf_reg['by_service'].keys()):
            for op in perf_reg['by_service'][svc]:
                if op.get('operation_id') == 'org-search-ods':
                    example_op = (svc, op)
                    break
            if example_op:
                break
        if not example_op:
            # fallback first op
            for svc in sorted(perf_reg['by_service'].keys()):
                if perf_reg['by_service'][svc]:
                    example_op = (svc, perf_reg['by_service'][svc][0])
                    break
    # Example control row: pick first available control from any registry except performance
    example_control = None
    for key, reg in registries.items():
        if key == 'performance':
            continue
        items = reg.get('items') or []
        if items:
            example_control = items[0]
            break
    lines.append("---")
    lines.append("## How to Read a Performance Operation Row (Plain English)")
    lines.append("")
    if example_op:
        svc, op = example_op
        op_row = "| {svc} | {op_id} | {cls} | {p50} | {p95} | {mx} | {burst} | {sustained} | {payload} | {status} | {rationale} |".format(
            svc=svc,
            op_id=op.get('operation_id',''),
            cls=op.get('performer_class',''),
            p50=op.get('p50_target_ms',''),
            p95=op.get('p95_target_ms',''),
            mx=op.get('absolute_max_ms',''),
            burst=op.get('burst_tps_target',''),
            sustained=op.get('sustained_tps_target',''),
            payload=op.get('max_request_payload_bytes',''),
            status=op.get('status',''),
            rationale=op.get('rationale','').replace('\n',' ').replace('|','/')
        )
        lines.append("Example row:")
        lines.append("")
        lines.append("| Service | Operation ID | Class | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |")
        lines.append("|---------|--------------|-------|--------|--------|--------|----------|--------------|---------------------|--------|-----------|")
        lines.append(op_row)
        lines.append("")
    lines.append("Meaning of columns:")
    lines.append("- Service: Subsystem owning the endpoint or job")
    lines.append("- Operation ID: Stable short name used in tests & dashboards")
    lines.append("- Class: Speed category (FAST snappy, STANDARD typical, SLOW heavy/background)")
    lines.append("- p50 ms: Typical median latency target")
    lines.append("- p95 ms: Near worst-case target for 95% of requests")
    lines.append("- Max ms: Hard cap; any single request over triggers alert/exception")
    lines.append("- Burst TPS: Short spike capacity target (blank = not defined yet)")
    lines.append("- Sustained TPS: Comfortable continuous throughput target (blank = not defined yet)")
    lines.append("- Max Payload (bytes): Largest allowed request size (blank = not constrained yet)")
    lines.append("- Status: draft (proposed), accepted (agreed/enforced), exception (temporarily unmet)")
    lines.append("- Rationale: Reasoning / assumptions behind targets")
    lines.append("")
    lines.append("Multiple tests per operation typically: latency monitor (p50/p95), max latency alert, throughput tests (burst & sustained), payload boundary test.")
    lines.append("")
    lines.append("---")
    lines.append("## How to Read a Control Row (Plain English)")
    lines.append("")
    if example_control:
        ctrl_row = "| {cid} | {nfr} | {measure} | {threshold} | {tooling} | {cadence} | {envs} | {services} | {status} | {rationale} |".format(
            cid=example_control.get('control_id',''),
            nfr=example_control.get('nfr_code',''),
            measure=example_control.get('measure','').replace('|','/').replace('\n',' '),
            threshold=example_control.get('threshold','').replace('|','/'),
            tooling=example_control.get('tooling',''),
            cadence=example_control.get('cadence',''),
            envs=",".join(example_control.get('environments', [])) if isinstance(example_control.get('environments'), list) else example_control.get('environments',''),
            services=",".join(example_control.get('services', [])) if isinstance(example_control.get('services'), list) else example_control.get('services',''),
            status=example_control.get('status',''),
            rationale=example_control.get('rationale','').replace('\n',' ').replace('|','/')
        )
        lines.append("Example control row:")
        lines.append("")
        lines.append("| Control ID | NFR Code | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |")
        lines.append("|------------|----------|---------|-----------|---------|---------|------|----------|--------|-----------|")
        lines.append(ctrl_row)
        lines.append("")
    lines.append("Meaning of columns:")
    lines.append("- Control ID: Stable name of the automated check")
    lines.append("- NFR Code: Which atomic NFR this control supports")
    lines.append("- Measure: What is examined (setting, scan result, metric)")
    lines.append("- Threshold: Quantified pass condition")
    lines.append("- Tooling: Automation or scanner enforcing the measure")
    lines.append("- Cadence: How often it runs (CI build, daily, per release)")
    lines.append("- Envs: Environments covered")
    lines.append("- Services: Scope (blank means all)")
    lines.append("- Status: draft / accepted / exception governance state")
    lines.append("- Rationale: Why the threshold/tool was chosen")
    lines.append("")
    lines.append("Typical validation: tool execution success, threshold met, alert on failure, exception tracked with mitigation & review date.")
    lines.append("")
    return "\n".join(lines) + "\n"

def main():
    if not MATRIX.exists():
        raise SystemExit(f"Matrix file not found: {MATRIX}")
    rows = parse_rows(MATRIX.read_text(encoding="utf-8"))
    if not rows:
        raise SystemExit("No rows parsed from matrix.")
    content = build_output(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(content, encoding="utf-8")
    print(f"Wrote simplified NFR page: {OUT}")

def load_story_jira_map() -> dict[str,str]:
    """Scan backlog stories and build map of story_id -> jira_key.

    If jira_key field empty but filename starts with a Jira key (e.g. FTRS-1234-...), use that.
    """
    mapping: dict[str,str] = {}
    if not BACKLOG_DIR.exists():
        return mapping
    for path in BACKLOG_DIR.glob("*.md"):
        try:
            head = path.read_text(encoding="utf-8").splitlines()[:40]
        except Exception:
            continue
        story_id = None
        jira_key = None
        for line in head:
            if line.startswith("story_id:"):
                story_id = line.split(":",1)[1].strip()
            elif line.startswith("jira_key:"):
                jira_key = line.split(":",1)[1].strip() or None
            if story_id and jira_key:
                break
        if not story_id:
            # attempt derive from filename (Jira-only file without story_id)
            fname = path.name
            if fname.startswith("FTRS-"):
                # treat entire key segment until next dash as jira
                jira_seg = fname.split('-')
                if len(jira_seg) >= 2:
                    jira_candidate = '-'.join(jira_seg[:2]) if jira_seg[1].isdigit() else jira_seg[0]
                    jira_key = jira_candidate if jira_candidate.startswith("FTRS-") else None
            continue
        if not jira_key:
            # derive from filename if pattern includes FTRS-####
            m = re.match(r"(FTRS-\d+)", path.name)
            if m:
                jira_key = m.group(1)
        if story_id and jira_key:
            mapping[story_id] = jira_key
    return mapping

if __name__ == "__main__":
    main()
