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
import json
from typing import Match
try:
    import yaml
except ModuleNotFoundError as e:
    raise SystemExit(
        "PyYAML is required to generate domain pages.\n"
        "Install it and re-run:\n\n"
        "  python3 -m venv .venv\n"
        "  source .venv/bin/activate\n"
        "  python3 -m pip install pyyaml\n"
        "  make nfrs-by-domain\n\n"
        "Alternatively: /opt/homebrew/bin/python3 -m pip install --user pyyaml"
    )

BACKLOG_DIR = Path("requirements/user-stories/backlog")

OUT = Path("docs/nfrs/nfr-by-domain.md")
# New: domain-specific output directory for split pages under docs/nfrs
DOMAIN_OUT_DIR = Path("docs/nfrs/nfr-by-domain")
EXPECTATIONS = Path("requirements/nfrs/performance/expectations.yaml")
DOMAIN_NFRS_DIR = Path("requirements/nfrs")
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
RE_JIRA = re.compile(r"\bFTRS-\d+\b")

def linkify_story_ids(text: str) -> str:
    """Convert any FTRS-#### occurrences to Jira hyperlinks.

    Example: FTRS-1234 -> [FTRS-1234](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1234)
    """
    if not isinstance(text, str) or not text:
        return text
    def _repl(m: Match[str]) -> str:
        key = m.group(0)
        return f"[{key}](https://nhsd-jira.digital.nhs.uk/browse/{key})"
    return RE_JIRA.sub(_repl, text)


def _append_blank_line(lines: list[str]) -> None:
    """Append a single blank line only if the previous line isn't already blank."""
    if not lines or lines[-1] != "":
        lines.append("")

def _collapse_blank_lines(lines: list[str]) -> list[str]:
    """Return a new list with multiple consecutive blank lines collapsed to one.

    A line is considered blank if its stripped content is empty. Preserves
    single blank separators and final single trailing newline when joined.
    """
    collapsed: list[str] = []
    last_blank = False
    for ln in lines:
        is_blank = (ln.strip() == "")
        if is_blank:
            if not last_blank:
                collapsed.append("")
            last_blank = True
        else:
            collapsed.append(ln)
            last_blank = False
    return collapsed

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
    _append_blank_line(lines)
    lines.append(f"Version: {reg['version']} Generated: {reg['generated']}")
    _append_blank_line(lines)
    lines.append("Below is a quick guide to the table columns:")
    _append_blank_line(lines)
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
    _append_blank_line(lines)
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
    _append_blank_line(lines)
    lines.append("(Refer to the domain expectations.yaml for additional metadata including evidence links and exception records.)")
    _append_blank_line(lines)

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
        lines: list[str] = [f"# FtRS NFR – {domain}", "", "This page is auto-generated; do not hand-edit.", ""]
        # NFR codes table (prefer domain nfrs.yaml if present)
        lines.append("## NFR Codes")
        lines.append("")
        # Checklist: Missing metadata in domain nfrs.yaml
        domain_yaml = DOMAIN_NFRS_DIR / domain.lower() / "nfrs.yaml"
        missing: list[str] = []
        if domain_yaml.exists():
            import yaml
            data = yaml.safe_load(domain_yaml.read_text(encoding="utf-8")) or {}
            for n in data.get("nfrs", []) or []:
                code = n.get("code", "UNKNOWN")
                expl = (n.get("explanation") or "").strip()
                stories = n.get("stories") or []
                if not expl:
                    missing.append(f"[Explanation] {code}")
                if not stories:
                    missing.append(f"[Stories] {code}")
        if missing:
            lines.append("### Missing Metadata Checklist")
            lines.append("")
            for m in missing:
                lines.append(f"- {m}")
            lines.append("")
        lines.append("| Code | Requirement | Explanation | Stories |")
        lines.append("|------|-------------|-------------|---------|")
        domain_yaml = DOMAIN_NFRS_DIR / domain.lower() / "nfrs.yaml"
        if domain_yaml.exists():
            import yaml
            data = yaml.safe_load(domain_yaml.read_text(encoding="utf-8")) or {}
            for n in data.get("nfrs", []):
                req = str(n.get("requirement","")).replace('|','/')
                expl = str(n.get("explanation","")) or explanations.get(n.get("code",""), "")
                expl = expl.replace('|','/').replace('\n',' ')
                stories_list = n.get("stories", [])
                stories_display_raw = ', '.join(stories_list) if stories_list else '(none)'
                stories_display = linkify_story_ids(stories_display_raw)
                lines.append(f"| {n.get('code','')} | {req} | {expl} | {stories_display} |")
        else:
            for r in rows:
                req = r['anchor'].replace('|','/')
                expl = explanations.get(r['code'], explanations.get('__error__', req)) or req
                expl = expl.replace('|','/').replace('\n',' ')
                stories_raw = r['stories']
                stories_list = [s.strip() for s in stories_raw.split(',') if s.strip() and s.strip() != '(none)']
                enriched: list[str] = []
                for s in stories_list:
                    base = s.split('(')[0].strip()
                    jira = story_jira_map.get(base)
                    if jira:
                        enriched.append(f"{base} ({jira})")
                    else:
                        enriched.append(base)
                stories_display = ', '.join(enriched) if enriched else '(none)'
                stories_display = linkify_story_ids(stories_display)
                lines.append(f"| {r['code']} | {req} | {expl} | {stories_display} |")
        lines.append("")
        # Collect gaps for a checklist section
        gaps: list[str] = []
        # Domain specific expectations
        if domain.lower() == "performance":
            lines.append("## Operations")
            _append_blank_line(lines)
            # Prefer operations embedded in nfrs.yaml
            domain_yaml = DOMAIN_NFRS_DIR / domain.lower() / "nfrs.yaml"
            ops_rows = []
            if domain_yaml.exists():
                import yaml
                data = yaml.safe_load(domain_yaml.read_text(encoding="utf-8")) or {}
                for n in data.get("nfrs", []):
                    for op in n.get("operations", []) or []:
                        ops_rows.append(op)
            # Fallback to expectations registry
            if not ops_rows:
                perf = registries.get("performance")
                if perf:
                    for svc in sorted(perf['by_service'].keys()):
                        ops_rows.extend(perf['by_service'][svc])
            lines.append("| Service | Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |")
            lines.append("|---------|--------------|--------|--------|--------|----------|--------------|---------------------|--------|-----------|")
            for op in ops_rows:
                svc = op.get('service') or op.get('service', '')
                op_id = op.get('operation_id')
                p50 = op.get('p50_target_ms')
                p95 = op.get('p95_target_ms')
                mx = op.get('absolute_max_ms')
                burst = op.get('burst_tps_target', '')
                sustained = op.get('sustained_tps_target', '')
                payload = op.get('max_request_payload_bytes', '')
                status = op.get('status')
                rationale = str(op.get('rationale','')).replace('\n',' ').replace('|','/')
                lines.append(f"| {svc} | {op_id} | {p50} | {p95} | {mx} | {burst} | {sustained} | {payload} | {status} | {rationale} |")
            # Single blank line after operations table
            if lines and lines[-1] != "":
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
                _append_blank_line(lines)
                for code in sorted(grouped.keys()):
                    lines.append(f"### {code}")
                    if code in explanations:
                        lines.append(explanations[code])
                    # Ensure exactly one blank before table
                    if lines and lines[-1] != "":
                        lines.append("")
                    lines.append("| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |")
                    lines.append("|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|")
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
                        lines.append(f"| [{code}](#{code.lower()}) | {ctrl} | {measure} | {threshold} | {tooling} | {cadence} | {envs} | {services} | {status} | {rationale} |")
                    # Single blank between groups
                    if lines and lines[-1] != "":
                        lines.append("")
                # If no controls exist for this NFR code in registry, surface NFR-level service scope when present
                domain_yaml_path = DOMAIN_NFRS_DIR / reg_key / "nfrs.yaml"
                if domain_yaml_path.exists():
                    try:
                        import yaml
                        dom_data = yaml.safe_load(domain_yaml_path.read_text(encoding="utf-8")) or {}
                        # find matching NFR entry
                        match = next((n for n in dom_data.get("nfrs", []) or [] if n.get("code") == code), None)
                        if match and (not grouped.get(code)):
                            nfr_services = match.get("services") or []
                            if isinstance(nfr_services, list) and nfr_services:
                                lines.append(
                                    "> No controls defined; NFR-level services: {}".format(
                                        ", ".join(sorted(nfr_services))
                                    )
                                )
                                _append_blank_line(lines)
                    except Exception:
                        pass
        # Sanitize trailing artifacts: remove stray code fences and collapse trailing blanks
        while lines and (lines[-1].strip() == "" or lines[-1].strip() == "```"):
            lines.pop()
        # Collapse any accidental multiple blanks before writing
        lines = _collapse_blank_lines(lines)
        lines.append("")
        content = "\n".join(lines) + "\n"
        # Final safeguard: collapse any 3+ consecutive newlines to 2 (single blank line)
        content = re.sub(r"\n{3,}", "\n\n", content)
        fname.write_text(content, encoding="utf-8")
        print(f"Wrote domain page: {fname}")
        # Debug: print last 3 lines written for lint diagnostics
        tail = Path(fname).read_text(encoding="utf-8").splitlines()
        tail_preview = " | ".join([l for l in tail[-3:]]) if len(tail) >= 3 else " | ".join(tail)
        print(f"TAIL:{domain}:{tail_preview}")

def build_output():
    # Build domains from schema-backed YAML files only
    domains_sorted: list[str] = []
    by_domain: dict[str, list[dict]] = {}
    for domain_yaml in DOMAIN_NFRS_DIR.glob("*/nfrs.yaml"):
        domain = domain_yaml.parent.name.capitalize()
        domains_sorted.append(domain)
        try:
            import yaml
            data = yaml.safe_load(domain_yaml.read_text(encoding="utf-8")) or {}
        except Exception:
            data = {}
        rows = []
        for n in (data.get("nfrs") or []):
            rows.append({
                "code": n.get("code",""),
                "domain": domain,
                "stories": ", ".join(n.get("stories") or []),
                "anchor": n.get("requirement",""),
            })
        # sort by code numeric
        rows.sort(key=sort_key)
        by_domain[domain] = rows
    # Omit volatile timestamp to keep commits clean
    lines = ["# FtRS NFR – By Domain", "", "This page is auto-generated; do not hand-edit.", ""]

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
        page_path = f"nfr-by-domain/{d.lower()}.md"
        lines.append(f"| {d} | {code_count} | {item_count} | [{d}]({page_path}) |")
    lines.append("")

    # Guard: warn if any codes missing explanations (excluding parse error fallback)
    if '__error__' not in explanations:
        all_codes: list[str] = []
        for domain_rows in by_domain.values():
            all_codes.extend([r['code'] for r in domain_rows])
        missing = sorted({c for c in all_codes if c not in explanations})
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
    lines.append("")
    # Ensure one blank before heading
    if lines and lines[-1] != "":
        lines.append("")
    lines.append("## How to Read a Performance Operation Row (Plain English)")
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
        lines.append("| Service | Operation ID | Class | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |")
        lines.append("|---------|--------------|-------|--------|--------|--------|----------|--------------|---------------------|--------|-----------|")
        lines.append(op_row)
        _append_blank_line(lines)
    # Ensure one blank before list intro
    if lines and lines[-1] != "":
        lines.append("")
    lines.append("Meaning of columns:")
    _append_blank_line(lines)
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
    # Ensure one blank after the list block
    if lines and lines[-1] != "":
        lines.append("")
    lines.append("Multiple tests per operation typically: latency monitor (p50/p95), max latency alert, throughput tests (burst & sustained), payload boundary test.")
    lines.append("")
    lines.append("---")
    lines.append("")
    # Ensure one blank before heading
    if lines and lines[-1] != "":
        lines.append("")
    lines.append("## How to Read a Control Row (Plain English)")
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
        lines.append("| Control ID | NFR Code | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |")
        lines.append("|------------|----------|---------|-----------|---------|---------|------|----------|--------|-----------|")
        lines.append(ctrl_row)
        _append_blank_line(lines)
    # Ensure one blank before list intro
    if lines and lines[-1] != "":
        lines.append("")
    lines.append("Meaning of columns:")
    _append_blank_line(lines)
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
    # Ensure one blank after the list block
    if lines and lines[-1] != "":
        lines.append("")
    lines.append("Typical validation: tool execution success, threshold met, alert on failure, exception tracked with mitigation & review date.")
    lines.append("")
    # Sanitize trailing artifacts: remove stray code fences and trailing blanks
    while lines and (lines[-1].strip() == "" or lines[-1].strip() == "```"):
        lines.pop()
    # Collapse any accidental multiple blanks in the index content
    lines = _collapse_blank_lines(lines)
    lines.append("")
    content = "\n".join(lines) + "\n"
    # Final safeguard: collapse any 3+ consecutive newlines to 2 (single blank line)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content

def main():
    content = build_output()
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
