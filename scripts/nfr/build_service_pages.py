#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
from collections import defaultdict
import re
from typing import Dict, List, Tuple
try:
    import yaml  # type: ignore
    YAML_AVAILABLE = True
except ModuleNotFoundError:
    YAML_AVAILABLE = False

ROOT = Path(__file__).resolve().parents[2]
# New structure under docs/nfrs
OUTPUT_DIR = ROOT / "docs" / "nfrs" / "nfr-by-service"
SERVICE_SUMMARY = ROOT / "docs" / "nfrs" / "nfr-by-service.md"
EXPLANATIONS_FILE = ROOT / "requirements" / "nfrs" / "cross-references" / "nfr-explanations.yaml"
DOMAIN_NFRS_DIR = ROOT / "requirements" / "nfrs"
def first_existing(*paths: Path) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None

def first_existing(*paths: Path) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None

REGISTRY_PATHS = {}

TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")
HEADING_CODE_RE = re.compile(r"^###\s+([A-Z]+-\d+)")

def _append_blank_line(lines: List[str]) -> None:
    if not lines or lines[-1] != "":
        lines.append("")

def load_matrix() -> Dict[str, Dict[str, str]]:
    """Matrix deprecated; YAML is the source of truth. Return empty mapping."""
    return {}

def load_domain_yaml(domain: str) -> dict:
    # If YAML library isn't available, skip loading.
    if not YAML_AVAILABLE:
        return {}
    path = DOMAIN_NFRS_DIR / domain / "nfrs.yaml"
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return data
    except Exception:
        return {}

def collect_services_from_yaml() -> Dict[str, dict]:
    """Collect service-centric data from domain YAML files.

    Returns map: service -> {
        'performance_ops': [op,...],
        'controls': {domain: {code: [control,...]}},
        'nfr_meta': {code: {'domain': domain, 'requirement': str, 'explanation': str, 'stories': str}},
    }
    Controls with empty services are considered universal and added to all discovered services.
    Services are discovered from performance operations and any control 'services' entries.
    """
    services: Dict[str, dict] = {}

    # Load performance operations from PERF domain YAML
    perf = load_domain_yaml('performance')
    all_services_set = set()
    for n in perf.get('nfrs', []) or []:
        for op in n.get('operations', []) or []:
            svc = op.get('service')
            if not svc:
                continue
            all_services_set.add(svc)
            bucket = services.setdefault(svc, {'performance_ops': [], 'controls': {}, 'nfr_meta': {}})
            bucket['performance_ops'].append(op)
            # Record PERF-001 meta for summary row
            code = n.get('code', 'PERF-001')
            bucket['nfr_meta'][code] = {
                'domain': 'Performance',
                'requirement': n.get('requirement', ''),
                'explanation': (n.get('explanation') or ''),
                'stories': ', '.join(n.get('stories') or []) or '(none)'
            }

    # No expectations fallback; YAML is the source of truth

    # Load controls from all other domains
    domain_dirs = [p.name for p in DOMAIN_NFRS_DIR.iterdir() if p.is_dir()]
    for domain in domain_dirs:
        data = load_domain_yaml(domain)
        for n in data.get('nfrs', []) or []:
            code = n.get('code', '')
            # Record meta for summary
            # Populate per domain regardless of controls to allow listing
            meta = {
                'domain': domain.capitalize(),
                'requirement': n.get('requirement', ''),
                'explanation': (n.get('explanation') or ''),
                'stories': ', '.join(n.get('stories') or []) or '(none)'
            }
            # controls handling
            ctrl_list = n.get('controls', []) or []
            # Determine target services: explicit list or universal
            target_services = set()
            explicit_any = False
            for c in ctrl_list:
                svcs = c.get('services')
                if isinstance(svcs, list) and svcs:
                    explicit_any = True
                    for s in svcs:
                        target_services.add(s)
                elif isinstance(svcs, str) and svcs.strip():
                    explicit_any = True
                    target_services.add(svcs.strip())
            if explicit_any:
                for svc in target_services:
                    all_services_set.add(svc)
                    bucket = services.setdefault(svc, {'performance_ops': [], 'controls': {}, 'nfr_meta': {}})
                    bucket['controls'].setdefault(domain.capitalize(), {}).setdefault(code, []).extend(ctrl_list)
                    bucket['nfr_meta'][code] = meta
            else:
                # No control-level services declared in controls.
                # If NFR declares services, attach meta to those services (summary only).
                nfr_services = n.get('services') or []
                if isinstance(nfr_services, list) and nfr_services:
                    for svc in nfr_services:
                        all_services_set.add(svc)
                        bucket = services.setdefault(svc, {'performance_ops': [], 'controls': {}, 'nfr_meta': {}})
                        bucket['nfr_meta'][code] = meta
                else:
                    # If there are actual controls but they are universal (no services), store them
                    # to be applied to all discovered services later. Do NOT add meta yet to avoid
                    # summary rows appearing without any controls or NFR-level services.
                    if ctrl_list:
                        services.setdefault('__universal__', {'performance_ops': [], 'controls': {}, 'nfr_meta': {}})
                        uni = services['__universal__']
                        uni['controls'].setdefault(domain.capitalize(), {}).setdefault(code, []).extend(ctrl_list)

    # Apply universal controls to all services discovered so far
    universal = services.pop('__universal__', None)
    if universal:
        for svc in all_services_set:
            bucket = services.setdefault(svc, {'performance_ops': [], 'controls': {}, 'nfr_meta': {}})
            for dom, codes in universal['controls'].items():
                for code, ctrls in codes.items():
                    bucket['controls'].setdefault(dom, {}).setdefault(code, []).extend(ctrls)
                    # ensure meta present
                    bucket['nfr_meta'].setdefault(code, universal['nfr_meta'].get(code, {}))

    return services

class DomainPage:
    def __init__(self, domain: str, lines: List[str]):
        self.domain = domain
        self.lines = lines
        self.nfr_map: Dict[str, Dict[str, str]] = {}
        self.controls: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self._parse()

    def _parse_table(self, start_idx: int) -> Tuple[List[str], int]:
        cols: List[str] = []
        rows: List[List[str]] = []
        i = start_idx
        # header line
        header = self.lines[i].strip()
        cols = [c.strip() for c in header.strip('|').split('|')]
        i += 1
        # separator line (---)
        if i < len(self.lines) and self.lines[i].strip().startswith('|'):
            i += 1
        # data rows
        while i < len(self.lines) and TABLE_ROW_RE.match(self.lines[i]):
            row = [c.strip() for c in self.lines[i].strip().strip('|').split('|')]
            # pad/truncate to header length
            if len(row) < len(cols):
                row = row + [''] * (len(cols) - len(row))
            elif len(row) > len(cols):
                row = row[:len(cols)]
            rows.append(row)
            i += 1
        return cols, rows, i

    def _parse(self) -> None:
        # Locate NFR Codes section
        i = 0
        while i < len(self.lines):
            if self.lines[i].strip() == "## NFR Codes":
                break
            i += 1
        # Skip until the table header
        while i < len(self.lines) and not TABLE_ROW_RE.match(self.lines[i]):
            i += 1
        if i >= len(self.lines):
            return
        cols, rows, i = self._parse_table(i)
        # Expect columns: Code | Requirement | Explanation | Stories
        try:
            code_idx = cols.index('Code')
            req_idx = cols.index('Requirement')
            exp_idx = cols.index('Explanation')
            stories_idx = cols.index('Stories')
        except ValueError:
            # Unexpected format; skip parsing
            return
        for r in rows:
            code = r[code_idx]
            self.nfr_map[code] = {
                'domain': self.domain,
                'requirement': r[req_idx],
                'explanation': r[exp_idx],
                'stories': r[stories_idx],
            }
        # Locate Controls section
        while i < len(self.lines) and self.lines[i].strip() != "## Controls":
            i += 1
        if i >= len(self.lines):
            return
        i += 1  # move past '## Controls'
        current_code: str | None = None
        while i < len(self.lines):
            line = self.lines[i].rstrip('\n')
            m = HEADING_CODE_RE.match(line)
            if m:
                current_code = m.group(1)
                i += 1
                # Skip description paragraph lines until table header
                while i < len(self.lines) and not self.lines[i].strip().startswith('| Control ID |'):
                    i += 1
                # Parse table for this code
                if i < len(self.lines) and self.lines[i].strip().startswith('| Control ID |'):
                    cols, rows, i = self._parse_table(i)
                    # Map expected columns
                    col_idx = {name: idx for idx, name in enumerate(cols)}
                    for r in rows:
                        entry = {
                            'control_id': r[col_idx.get('Control ID', 0)],
                            'measure': r[col_idx.get('Measure', 1)],
                            'threshold': r[col_idx.get('Threshold', 2)],
                            'tooling': r[col_idx.get('Tooling', 3)],
                            'cadence': r[col_idx.get('Cadence', 4)],
                            'envs': r[col_idx.get('Envs', 5)],
                            'services': r[col_idx.get('Services', 6)],
                            'status': r[col_idx.get('Status', 7)],
                            'rationale': r[col_idx.get('Rationale', 8)],
                        }
                        self.controls[current_code].append(entry)
                continue
            i += 1


def collect_service_map() -> Dict[str, List[Dict[str, str]]]:
    RE_JIRA = re.compile(r"\bFTRS-\d+\b")

    def linkify_story_ids(text: str) -> str:
        if not isinstance(text, str) or not text:
            return text
        def _repl(m: re.Match) -> str:
            key = m.group(0)
            return f"[{key}](https://nhsd-jira.digital.nhs.uk/browse/{key})"
        return RE_JIRA.sub(_repl, text)
    service_map: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    # Prefer YAML registries for source-of-truth controls if available
    if YAML_AVAILABLE:
        # First, try YAML-only discovery
        yaml_services = collect_services_from_yaml()
        if yaml_services:
            for svc, payload in yaml_services.items():
                # Summary meta rows (one per NFR code)
                for code, meta in payload.get('nfr_meta', {}).items():
                    service_map[svc].append({
                        'domain': meta.get('domain',''),
                        'code': code,
                        'requirement': meta.get('requirement',''),
                        'explanation': meta.get('explanation',''),
                        'stories': linkify_story_ids(meta.get('stories','')),
                        'service': svc,
                    })
                # Controls rows
                for dom, codes in payload.get('controls', {}).items():
                    for code, ctrls in codes.items():
                        for c in ctrls:
                            envs_val = c.get('environments', '')
                            envs = ",".join(envs_val) if isinstance(envs_val, list) else envs_val
                            service_map[svc].append({
                                'domain': dom,
                                'code': code,
                                'requirement': payload.get('nfr_meta', {}).get(code, {}).get('requirement',''),
                                'explanation': payload.get('nfr_meta', {}).get(code, {}).get('explanation',''),
                                'stories': linkify_story_ids(payload.get('nfr_meta', {}).get(code, {}).get('stories','')),
                                'control_id': c.get('control_id',''),
                                'measure': c.get('measure',''),
                                'threshold': c.get('threshold',''),
                                'tooling': c.get('tooling',''),
                                'cadence': c.get('cadence',''),
                                'envs': envs,
                                'services': svc,
                                'status': c.get('status',''),
                                'rationale': str(c.get('rationale','')).replace('\n',' ').replace('|','/'),
                                'service': svc,
                            })
            if service_map:
                return service_map
        explanations: Dict[str, str] = {}
        matrix_map: Dict[str, Dict[str, str]] = load_matrix()
        if EXPLANATIONS_FILE.exists():
            try:
                exp_data = yaml.safe_load(EXPLANATIONS_FILE.read_text(encoding="utf-8")) or {}
                explanations = (exp_data.get("explanations") or {})
            except Exception:
                explanations = {}
        for domain_name, path in REGISTRY_PATHS.items():
            if not path.exists():
                continue
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            items = data.get("controls") or []
            for c in items:
                code = c.get("nfr_code", "")
                # Canonical requirement & stories from the matrix (matches domain page logic)
                matrix_entry = matrix_map.get(code, {"requirement": "", "stories": ""})
                measure = c.get("measure", "")
                threshold = c.get("threshold", "")
                tooling = c.get("tooling", "")
                cadence = c.get("cadence", "")
                envs_val = c.get("environments", "")
                envs = ",".join(envs_val) if isinstance(envs_val, list) else envs_val
                services_val = c.get("services", [])
                services_list = services_val if isinstance(services_val, list) else [s.strip() for s in str(services_val).split(',') if s.strip()]
                status = c.get("status", "")
                rationale = str(c.get("rationale", "")).replace("\n"," ")
                # Requirement text for the summary: use matrix anchor; Explanation from explanations.yaml
                req_text = matrix_entry.get("requirement", "")
                stories_text = linkify_story_ids(matrix_entry.get("stories", ""))
                for s in services_list:
                    service_map[s].append({
                        'domain': domain_name,
                        'code': code,
                        'requirement': req_text,
                        'explanation': explanations.get(code, ''),
                        'stories': stories_text,
                        'control_id': c.get('control_id',''),
                        'measure': measure,
                        'threshold': threshold,
                        'tooling': tooling,
                        'cadence': cadence,
                        'envs': envs,
                        'services': s,
                        'status': status,
                        'rationale': rationale,
                        'service': s,
                    })
        # Additionally, prefer domain-level nfrs.yaml when present (controls embedded per NFR)
        for domain_dir in DOMAIN_NFRS_DIR.iterdir():
            if not domain_dir.is_dir():
                continue
            nfrs_yaml = domain_dir / "nfrs.yaml"
            if not nfrs_yaml.exists():
                continue
            try:
                nfrs_data = yaml.safe_load(nfrs_yaml.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            for nfr in nfrs_data.get("nfrs", []):
                code = nfr.get("code", "")
                domain_name = domain_dir.name
                req_text = nfr.get("requirement", "")
                expl_text = nfr.get("explanation", "")
                stories_list = nfr.get("stories", [])
                stories_text = linkify_story_ids(", ".join(stories_list) if stories_list else "(none)")
                for ctrl in nfr.get("controls", []):
                    services_list = ctrl.get("services", [])
                    envs_list = ctrl.get("environments", [])
                    envs = ",".join(envs_list) if isinstance(envs_list, list) else envs_list
                    for s in services_list:
                        service_map[s].append({
                            'domain': domain_name,
                            'code': code,
                            'requirement': req_text,
                            'explanation': expl_text,
                            'stories': stories_text,
                            'control_id': ctrl.get('control_id',''),
                            'measure': ctrl.get('measure',''),
                            'threshold': ctrl.get('threshold',''),
                            'tooling': ctrl.get('tooling',''),
                            'cadence': ctrl.get('cadence',''),
                            'envs': envs,
                            'services': s,
                            'status': ctrl.get('status',''),
                            'rationale': str(ctrl.get('rationale','')).replace('\n',' ').replace('|','/'),
                            'service': s,
                        })
        # If YAML provided no entries (unlikely), fall back to domain pages
        if service_map:
            return service_map
    # Fallback: parse domain pages
    # Fallback to legacy domain pages only if present (deprecated)
    source_dir = ROOT / "docs" / "nfrs" / "nfr-by-domain"
    fallback_dir = ROOT / "docs" / "developer-guides" / "nfr-domains"
    source_dir = source_dir if source_dir.exists() and any(source_dir.glob('*.md')) else fallback_dir
    for md in sorted(source_dir.glob('*.md')):
        domain = md.stem
        lines = md.read_text(encoding='utf-8').splitlines()
        page = DomainPage(domain, lines)
        for code, entries in page.controls.items():
            nfr = page.nfr_map.get(code, {'domain': domain, 'requirement': '', 'explanation': '', 'stories': ''})
            for e in entries:
                services = [s.strip() for s in e.get('services', '').split(',') if s.strip()]
                for s in services:
                    service_map[s].append({
                        'domain': nfr['domain'],
                        'code': code,
                        'requirement': nfr['requirement'],
                        'explanation': nfr.get('explanation',''),
                        'stories': nfr['stories'],
                        **e,
                        'service': s,
                    })
    return service_map


def write_service_pages(service_map: Dict[str, List[Dict[str, str]]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for service, items in sorted(service_map.items()):
        # Deduplicate summary rows per code
        seen_codes = set()
        summary_rows: List[Tuple[str, str, str, str, str]] = []
        for it in items:
            key = it['code']
            if key not in seen_codes:
                summary_rows.append((it['domain'], it['code'], it['requirement'], it.get('explanation',''), it['stories']))
                seen_codes.add(key)
        # Group controls by code (filter out summary-only items without control fields)
        by_code: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        for it in items:
            if 'control_id' in it:
                by_code[it['code']].append(it)
        # Optional: Performance operations for this service (prefer domain nfrs.yaml operations)
        perf_ops: List[Dict[str, str]] = []
        perf_nfrs_yaml = DOMAIN_NFRS_DIR / "performance" / "nfrs.yaml"
        if YAML_AVAILABLE and perf_nfrs_yaml.exists():
            try:
                perf_nfrs = yaml.safe_load(perf_nfrs_yaml.read_text(encoding="utf-8")) or {}
                for n in perf_nfrs.get("nfrs", []):
                    for op in n.get("operations", []) or []:
                        svc_val = str(op.get("service",""))
                        if svc_val.strip().lower() == service.strip().lower():
                            perf_ops.append(op)
            except Exception:
                perf_ops = []
        # Fallback: parse performance domain page Operations table (deprecated)
        if not perf_ops:
            dom_dir = ROOT / "docs" / "nfrs" / "nfr-by-domain"
            fallback_dom = ROOT / "docs" / "developer-guides" / "nfr-domains"
            perf_md = (dom_dir / "performance.md") if (dom_dir / "performance.md").exists() else (fallback_dom / "performance.md")
            if perf_md.exists():
                lines_perf = perf_md.read_text(encoding='utf-8').splitlines()
                # locate header row starting with | Service |
                j = 0
                while j < len(lines_perf) and lines_perf[j].strip() != "## Operations":
                    j += 1
                if j < len(lines_perf):
                    j += 1
                    # find the table header
                    while j < len(lines_perf) and not lines_perf[j].strip().startswith('| Service |'):
                        j += 1
                    if j < len(lines_perf):
                        # header and separator
                        header = lines_perf[j].strip().strip('|').split('|')
                        j += 2  # skip separator line
                        # rows
                        while j < len(lines_perf) and TABLE_ROW_RE.match(lines_perf[j]):
                            cells = [c.strip() for c in lines_perf[j].strip().strip('|').split('|')]
                            row = {}
                            for idx, name in enumerate(['Service','Operation ID','p50 ms','p95 ms','Max ms','Burst TPS','Sustained TPS','Max Payload (bytes)','Status','Rationale']):
                                if idx < len(cells):
                                    row[name] = cells[idx]
                            if row.get('Service','').strip().lower() == service.strip().lower():
                                perf_ops.append({
                                    'operation_id': row.get('Operation ID',''),
                                    'p50_target_ms': row.get('p50 ms',''),
                                    'p95_target_ms': row.get('p95 ms',''),
                                    'absolute_max_ms': row.get('Max ms',''),
                                    'burst_tps_target': row.get('Burst TPS',''),
                                    'sustained_tps_target': row.get('Sustained TPS',''),
                                    'max_request_payload_bytes': row.get('Max Payload (bytes)',''),
                                    'status': row.get('Status',''),
                                    'rationale': row.get('Rationale',''),
                                })
                            j += 1
        # Performance summary rows are already derived from YAML in collect_service_map

        # Build markdown
        md: List[str] = []
        md.append(f"# FtRS NFR – Service: {service}")
        _append_blank_line(md)
        md.append("Source: docs/nfrs/nfr-by-domain/* (derived)")
        _append_blank_line(md)
        md.append("This page is auto-generated; do not hand-edit.")
        _append_blank_line(md)
        md.append("## Summary")
        _append_blank_line(md)
        md.append("| Domain | Code | Requirement | Explanation | Stories |")
        md.append("|--------|------|-------------|-------------|---------|")
        for domain, code, req, expl, stories in sorted(summary_rows, key=lambda r: (r[0], r[1])):
            md.append(f"| {domain} | {code} | {req} | {expl} | {stories} |")
        _append_blank_line(md)
        # Remove old duplicate injection block; performance rows are already in summary_rows above

        # Always render an Operations section; show a hint if none found
        md.append("## Operations")
        _append_blank_line(md)
        if perf_ops:
            md.append("| Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |")
            md.append("|--------------|--------|--------|--------|-----------|---------------|---------------------|--------|-----------|")
            for op in sorted(perf_ops, key=lambda o: o.get("operation_id","")):
                row = [
                    str(op.get("operation_id","")),
                    str(op.get("p50_target_ms","")),
                    str(op.get("p95_target_ms","")),
                    str(op.get("absolute_max_ms","")),
                    str(op.get("burst_tps_target","")),
                    str(op.get("sustained_tps_target","")),
                    str(op.get("max_request_payload_bytes","")),
                    str(op.get("status","")),
                    str(op.get("rationale","")).replace("\n"," ").replace("|","/")
                ]
                md.append('| ' + ' | '.join(row) + ' |')
            _append_blank_line(md)
        else:
            md.append("No performance operations defined for this service.")
            _append_blank_line(md)

        md.append("## Controls")
        _append_blank_line(md)
        for code in sorted(by_code.keys()):
            # Find requirement blurb from first item
            req = by_code[code][0].get('requirement','')
            md.append(f"### {code}")
            _append_blank_line(md)
            md.append(req)
            _append_blank_line(md)
            md.append("| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |")
            md.append("|------------|---------|-----------|---------|---------|------|----------|--------|-----------|")
            for it in by_code[code]:
                # For clarity, set Services column to this service only
                row = [
                    it.get('control_id',''), it.get('measure',''), it.get('threshold',''), it.get('tooling',''), it.get('cadence',''),
                    it.get('envs',''), service, it.get('status',''), it.get('rationale','')
                ]
                md.append('| ' + ' | '.join(row) + ' |')
            _append_blank_line(md)
        out_path = OUTPUT_DIR / f"{service}.md"
        out_path.write_text('\n'.join(md), encoding='utf-8')


def write_service_summary(service_map: Dict[str, List[Dict[str, str]]]) -> None:
    SERVICE_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# FtRS NFR – By Service")
    lines.append("")
    lines.append("This page is auto-generated; do not hand-edit.")
    lines.append("")
    lines.append("| Service | Page |")
    lines.append("|---------|------|")
    for service in sorted(service_map.keys()):
        rel = f"nfr-by-service/{service}.md"
        lines.append(f"| {service} | [{service}]({rel}) |")
    lines.append("")
    SERVICE_SUMMARY.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    service_map = collect_service_map()
    write_service_pages(service_map)
    write_service_summary(service_map)
    print(f"Generated {len(service_map)} service pages in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
