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
SOURCES_FILE = ROOT / "requirements" / "nfrs" / "cross-references" / "nfr-sources.yaml"
DOMAIN_NFRS_DIR = ROOT / "requirements" / "nfrs"
SERVICES_REGISTRY = DOMAIN_NFRS_DIR / "services.yaml"
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

def load_service_display_names() -> Dict[str, str]:
    """Load mapping of internal service ids to human-friendly names."""
    mapping: Dict[str, str] = {}
    try:
        if SERVICES_REGISTRY.exists() and YAML_AVAILABLE:
            data = yaml.safe_load(SERVICES_REGISTRY.read_text(encoding="utf-8")) or {}
            for k, v in (data.get("services") or {}).items():
                if isinstance(k, str) and isinstance(v, str):
                    mapping[k.strip()] = v.strip()
    except Exception:
        pass
    return mapping

def load_operation_display_names() -> Dict[str, Dict[str, str]]:
    mapping: Dict[str, Dict[str, str]] = {}
    try:
        if SERVICES_REGISTRY.exists() and YAML_AVAILABLE:
            data = yaml.safe_load(SERVICES_REGISTRY.read_text(encoding="utf-8")) or {}
            ops = data.get("operations") or {}
            for svc, m in ops.items():
                if isinstance(m, dict):
                    mapping[svc] = {}
                    for op_id, disp in m.items():
                        if isinstance(op_id, str) and isinstance(disp, str):
                            mapping[svc][op_id.strip()] = disp.strip()
    except Exception:
        pass
    return mapping

def load_nfr_sources() -> Dict[str, List[Dict[str,str]]]:
    mapping: Dict[str, List[Dict[str,str]]] = {}
    try:
        if SOURCES_FILE.exists() and YAML_AVAILABLE:
            data = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8")) or {}
            srcs = data.get("sources") or {}
            if isinstance(srcs, dict):
                for code, entries in srcs.items():
                    if not isinstance(entries, list):
                        continue
                    arr: List[Dict[str,str]] = []
                    for e in entries:
                        if isinstance(e, dict):
                            title = str(e.get("title",""))
                            path = str(e.get("path",""))
                            anchor = str(e.get("anchor","")) if e.get("anchor") else ""
                            if title and path:
                                arr.append({"title": title, "path": path, "anchor": anchor})
                    if arr:
                        mapping[str(code)] = arr
    except Exception:
        pass
    return mapping

def format_story_list(keys: List[str]) -> str:
    if not keys:
        return "(none)"
    items: List[str] = []
    for k in keys:
        items.append(f"[{k}](https://nhsd-jira.digital.nhs.uk/browse/{k})")
    return ", ".join(items)

def load_domain_sources() -> Dict[str, List[Dict[str,str]]]:
    mapping: Dict[str, List[Dict[str,str]]] = {}
    try:
        if SOURCES_FILE.exists() and YAML_AVAILABLE:
            data = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8")) or {}
            domains = data.get("domains") or {}
            if isinstance(domains, dict):
                for dom, entries in domains.items():
                    if not isinstance(entries, list):
                        continue
                    arr: List[Dict[str,str]] = []
                    for e in entries:
                        if isinstance(e, dict):
                            title = str(e.get("title",""))
                            url = str(e.get("url",""))
                            if title and url:
                                arr.append({"title": title, "url": url})
                    if arr:
                        mapping[str(dom).capitalize()] = arr
    except Exception:
        pass
    return mapping

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
            # Track whether any control declares services explicitly
            explicit_any = False
            # Assign each control only to its declared services
            for c in ctrl_list:
                svcs = c.get('services')
                current_svcs: List[str] = []
                if isinstance(svcs, list) and svcs:
                    current_svcs = [str(s).strip() for s in svcs if str(s).strip()]
                elif isinstance(svcs, str) and svcs.strip():
                    current_svcs = [svcs.strip()]
                if current_svcs:
                    explicit_any = True
                    for svc in current_svcs:
                        all_services_set.add(svc)
                        bucket = services.setdefault(svc, {'performance_ops': [], 'controls': {}, 'nfr_meta': {}})
                        bucket['controls'].setdefault(domain.capitalize(), {}).setdefault(code, []).append(c)
                        # Ensure meta present for this NFR code for this service
                        bucket['nfr_meta'][code] = meta
            if not explicit_any:
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
                            'control_id': r[col_idx.get('Control ID', 0)] if 'Control ID' in col_idx else '',
                            'measure': r[col_idx.get('Measure', 1)] if 'Measure' in col_idx else '',
                            'threshold': r[col_idx.get('Threshold', 2)] if 'Threshold' in col_idx else '',
                            'cadence': r[col_idx.get('Cadence', 3)] if 'Cadence' in col_idx else '',
                            'envs': r[col_idx.get('Envs', 4)] if 'Envs' in col_idx else '',
                            'services': r[col_idx.get('Services', 5)] if 'Services' in col_idx else '',
                            'status': r[col_idx.get('Status', 6)] if 'Status' in col_idx else '',
                            'rationale': r[col_idx.get('Rationale', 7)] if 'Rationale' in col_idx else '',
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
                            # Prefer control-level stories when present; else fall back to NFR-level meta stories
                            ctrl_stories = c.get('stories', []) if isinstance(c.get('stories'), list) else []
                            stories_val = ', '.join(ctrl_stories) if ctrl_stories else payload.get('nfr_meta', {}).get(code, {}).get('stories','')
                            service_map[svc].append({
                                'domain': dom,
                                'code': code,
                                'requirement': payload.get('nfr_meta', {}).get(code, {}).get('requirement',''),
                                'explanation': payload.get('nfr_meta', {}).get(code, {}).get('explanation',''),
                                'stories': linkify_story_ids(stories_val),
                                'control_id': c.get('control_id',''),
                                'operation_id': c.get('operation_id',''),
                                'measure': c.get('measure',''),
                                'threshold': c.get('threshold',''),
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
    service_names = load_service_display_names()
    op_names = load_operation_display_names()
    nfr_sources = load_nfr_sources()
    domain_sources = load_domain_sources()
    # Optional: load plain-language explanations for cross-linking
    explanations: Dict[str, str] = {}
    if YAML_AVAILABLE and EXPLANATIONS_FILE.exists():
        try:
            import yaml  # type: ignore
            exp_data = yaml.safe_load(EXPLANATIONS_FILE.read_text(encoding="utf-8")) or {}
            explanations = (exp_data.get("explanations") or {})
        except Exception:
            explanations = {}
    def display_service(s: str) -> str:
        return service_names.get(s, s)
    def display_operation(svc: str, op_id: str) -> str:
        disp = op_names.get(svc, {}).get(op_id)
        return f"{disp} ({op_id})" if disp else op_id

    def page_title_for(service_disp: str, dom: str) -> str:
        dom_tc = dom.capitalize()
        suffix = "NFRs & Operations" if dom_tc == "Performance" else "NFRs & Controls"
        return f"{service_disp} – {dom_tc} {suffix}"

    def anchor_prefix_from_title(title: str) -> str:
        # Confluence heading anchors squash spaces but retain punctuation/dashes
        return (title or "").replace(" ", "")
    for service, items in sorted(service_map.items()):
        service_dir = OUTPUT_DIR / service
        service_dir.mkdir(parents=True, exist_ok=True)
        # Build union of stories per code across NFR-level and control-level entries
        _re_jira = re.compile(r"\bFTRS-\d+\b")
        stories_by_code: Dict[str, set] = defaultdict(set)
        for it in items:
            code = it.get('code')
            s = it.get('stories')
            if isinstance(code, str) and isinstance(s, str) and s:
                for m in _re_jira.findall(s):
                    stories_by_code[code].add(m)
        # Deduplicate summary rows per code, using unioned stories
        seen_codes = set()
        summary_rows: List[Tuple[str, str, str, str, str]] = []
        for it in items:
            key = it['code']
            if key not in seen_codes:
                union_keys = sorted(list(stories_by_code.get(key, set())))
                stories_cell = format_story_list(union_keys)
                summary_rows.append((it['domain'], it['code'], it['requirement'], it.get('explanation',''), stories_cell))
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
        # Merge duplicate operation entries across PERF-001/011/012/013 by operation_id
        merged_ops: Dict[str, Dict[str, str]] = {}
        def _set_if_empty(target: Dict[str,str], key: str, val: str) -> None:
            if val not in (None, "") and not target.get(key):
                target[key] = val
        def _merge_op(dst: Dict[str,str], src: Dict[str,str]) -> None:
            for k in [
                'p50_target_ms','p95_target_ms','absolute_max_ms',
                'burst_tps_target','sustained_tps_target','max_request_payload_bytes',
                'status','rationale'
            ]:
                _set_if_empty(dst, k, str(src.get(k, "")))
            # Merge stories arrays
            s = src.get('stories') or []
            if isinstance(s, list) and s:
                cur = dst.setdefault('stories', [])
                for it in s:
                    if it not in cur:
                        cur.append(it)
        for op in perf_ops:
            op_id = str(op.get('operation_id','')).strip()
            if not op_id:
                continue
            if op_id not in merged_ops:
                merged_ops[op_id] = {
                    'operation_id': op_id,
                    'service': op.get('service','')
                }
            _merge_op(merged_ops[op_id], op)
        perf_ops = list(merged_ops.values())
        # Build an operation lookup to correlate controls with targets
        op_lookup: Dict[str, Dict[str, str]] = {op['operation_id']: op for op in perf_ops if op.get('operation_id')}

        # Write minimal index.md under the service directory (no local child links; Confluence will render children)
        index_md: List[str] = []
        index_md.append(f"# FtRS NFR – Service: {display_service(service)}")
        _append_blank_line(index_md)
        index_md.append("This page is auto-generated; do not hand-edit.")
        _append_blank_line(index_md)
        (service_dir / "index.md").write_text('\n'.join(index_md), encoding='utf-8')
        # Clean up any legacy single-file output
        legacy_path = OUTPUT_DIR / f"{service}.md"
        if legacy_path.exists():
            try:
                legacy_path.unlink()
            except Exception:
                pass

        # Now write domain-specific pages for this service
        # Helper to render Operations table (Performance domain only)
        def _render_operations(lines: List[str]) -> None:
            lines.append("## Operations")
            _append_blank_line(lines)
            lines.append("Operation: performance-specific expectation for an endpoint or job. Tied to a service and operation_id; sets p50/p95 latency, absolute max, burst/sustained TPS, payload limits, status, rationale, and stories.")
            _append_blank_line(lines)
            if perf_ops:
                lines.append("| Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Stories | Rationale |")
                lines.append("|--------------|--------|--------|--------|-----------|---------------|---------------------|--------|---------|-----------|")
                for op in sorted(perf_ops, key=lambda o: o.get("operation_id","")):
                    row = [
                        display_operation(service, str(op.get("operation_id",""))),
                        str(op.get("p50_target_ms","")),
                        str(op.get("p95_target_ms","")),
                        str(op.get("absolute_max_ms","")),
                        str(op.get("burst_tps_target","")),
                        str(op.get("sustained_tps_target","")),
                        str(op.get("max_request_payload_bytes","")),
                        str(op.get("status","")),
                        format_story_list(sorted(set([s for s in (op.get("stories") or []) if isinstance(s, str)]))),
                        str(op.get("rationale","")),
                    ]
                    lines.append('| ' + ' | '.join(row) + ' |')
                _append_blank_line(lines)
            else:
                lines.append("No performance operations defined for this service.")
                _append_blank_line(lines)

        # Build domain -> codes mapping for controls
        codes_by_domain: Dict[str, Dict[str, List[Dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
        for code, entries in by_code.items():
            for it in entries:
                dom = str(it.get('domain','')).capitalize()
                codes_by_domain[dom][code].append(it)

        for dom in sorted({d for (d, _, _, _, _) in summary_rows}):
            dom_file = service_dir / f"{dom.lower()}.md"
            dmd: List[str] = []
            dmd.append(f"# FtRS NFR – Service: {display_service(service)} – Domain: {dom}")
            _append_blank_line(dmd)
            dmd.append("Source: docs/nfrs/nfr-by-domain/* (derived)")
            _append_blank_line(dmd)
            dmd.append("This page is auto-generated; do not hand-edit.")
            _append_blank_line(dmd)
            # Optional domain-level sources (e.g., original Confluence pages)
            dom_sources = domain_sources.get(dom, [])
            if dom_sources:
                dmd.append("## Domain Sources")
                _append_blank_line(dmd)
                for s in dom_sources:
                    dmd.append(f"- [{s['title']}]({s['url']})")
                _append_blank_line(dmd)
            # Summary for this domain
            dmd.append("## Summary")
            _append_blank_line(dmd)
            dmd.append("| Domain | Code | Requirement | Explanation | Stories |")
            dmd.append("|--------|------|-------------|-------------|---------|")
            by_code_dom = codes_by_domain.get(dom, {})
            codes_with_controls_dom = set(by_code_dom.keys())
            # Compute page-title-prefixed anchor base expected by Confluence for headings
            title_prefix = anchor_prefix_from_title(page_title_for(display_service(service), dom))
            for domain, code, req, expl, stories in sorted([r for r in summary_rows if r[0] == dom], key=lambda r: r[1]):
                # Link code to the on-page Controls section using Confluence auto heading anchor
                code_cell = f"[{code}](#{title_prefix}-{code.upper()})"
                dmd.append(f"| {domain} | {code_cell} | {req} | {expl} | {stories} |")
            _append_blank_line(dmd)
            # Operations only for Performance domain
            if dom.lower() == 'performance':
                _render_operations(dmd)
            # Controls for this domain
            dmd.append("## Controls")
            _append_blank_line(dmd)
            dmd.append("Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.")
            _append_blank_line(dmd)
            for code in sorted(by_code_dom.keys()):
                req = by_code_dom[code][0].get('requirement','')
                dmd.append(f"### {code}")
                _append_blank_line(dmd)
                dmd.append(req)
                _append_blank_line(dmd)
                # Link to central explanations page to avoid cluttering service pages
                if code in explanations:
                    dmd.append(f"See explanation: [{code}](../../explanations.md#Explanations-{code.upper()})")
                    _append_blank_line(dmd)
                # Sources for this NFR code if available
                srcs = nfr_sources.get(code, [])
                if srcs:
                    links = []
                    for s in srcs:
                        href = s["path"] + (f"#{s['anchor']}" if s.get("anchor") else "")
                        links.append(f"[{s['title']}]({href})")
                    dmd.append("Sources: " + ", ".join(links))
                    _append_blank_line(dmd)
                # Dynamically select columns based on domain/code
                perf_code = code.upper()
                base_cols = ["Control ID","Measure","Threshold","Cadence","Envs","Services","Status","Stories"]
                extra_cols: List[str] = []
                if dom.lower() == 'performance':
                    if perf_code == 'PERF-001':
                        extra_cols = ["Operation ID","p50 ms","p95 ms","Max ms"]
                    elif perf_code == 'PERF-011':
                        extra_cols = ["Operation ID","Burst TPS"]
                    elif perf_code == 'PERF-012':
                        extra_cols = ["Operation ID","Sustained TPS"]
                    elif perf_code == 'PERF-013':
                        extra_cols = ["Operation ID","Max Payload (bytes)"]
                header_cols = base_cols + extra_cols + ["Rationale"]
                dmd.append('| ' + ' | '.join(header_cols) + ' |')
                dmd.append('|'+ '|'.join('-' * len(c) for c in header_cols) + '|')
                for it in by_code_dom[code]:
                    ctrl_id = it.get('control_id','')
                    op_hint = str(it.get('operation_id','')).strip()
                    matched_op: Dict[str,str] | None = None
                    if op_hint and op_hint in op_lookup:
                        matched_op = op_lookup[op_hint]
                    else:
                        # For PERF-011/012/013, avoid heuristic single-op match so we can expand per operation
                        allow_heuristic = not (dom.lower() == 'performance' and perf_code in ('PERF-011','PERF-012','PERF-013'))
                        if allow_heuristic:
                            for op_id, op in op_lookup.items():
                                if op_id and (op_id in ctrl_id or op_id in it.get('measure','')):
                                    matched_op = op
                                    break
                    op_id_raw = str(matched_op.get('operation_id','')) if matched_op else ''
                    op_id_val = display_operation(service, op_id_raw) if op_id_raw else ''
                    p50 = str(matched_op.get('p50_target_ms','')) if matched_op else ''
                    p95 = str(matched_op.get('p95_target_ms','')) if matched_op else ''
                    mx = str(matched_op.get('absolute_max_ms','')) if matched_op else ''
                    burst = str(matched_op.get('burst_tps_target','')) if matched_op else ''
                    sustained = str(matched_op.get('sustained_tps_target','')) if matched_op else ''
                    payload = str(matched_op.get('max_request_payload_bytes','')) if matched_op else ''
                    ctrl_stories_val = it.get('stories')
                    op_stories_val = ''
                    if matched_op:
                        op_stories = matched_op.get('stories') or []
                        if isinstance(op_stories, list) and op_stories:
                            op_keys = sorted(set([s for s in op_stories if isinstance(s, str)]))
                            op_stories_val = format_story_list(op_keys)
                    prefer_op = (str(it.get('domain','')).lower() == 'performance' and str(it.get('code','')).upper() == 'PERF-001')
                    if prefer_op:
                        if op_stories_val:
                            stories_cell = op_stories_val
                        else:
                            ctrl_keys = sorted(set(re.findall(r"\bFTRS-\d+\b", ctrl_stories_val or "")))
                            stories_cell = format_story_list(ctrl_keys)
                    else:
                        if isinstance(ctrl_stories_val, str) and ctrl_stories_val.strip():
                            ctrl_keys = sorted(set(re.findall(r"\bFTRS-\d+\b", ctrl_stories_val)))
                            stories_cell = format_story_list(ctrl_keys)
                        elif op_stories_val:
                            stories_cell = op_stories_val
                        else:
                            stories_cell = "(none)"
                    base_row = [
                        ctrl_id, it.get('measure',''), it.get('threshold',''), it.get('cadence',''),
                        it.get('envs',''), display_service(service), it.get('status',''), (stories_cell or "(none)")
                    ]
                    extra_row: List[str] = []
                    if dom.lower() == 'performance':
                        if perf_code == 'PERF-001':
                            extra_row = [op_id_val, p50, p95, mx]
                        elif perf_code == 'PERF-011':
                            # If no matched operation and no explicit hint, expand into one row per operation for this service
                            if not matched_op and not op_hint:
                                for oid, op in sorted(op_lookup.items()):
                                    oid_disp = display_operation(service, oid) if oid else ''
                                    burst_val = str(op.get('burst_tps_target',''))
                                    row = base_row + [oid_disp, burst_val] + [it.get('rationale','')]
                                    dmd.append('| ' + ' | '.join(row) + ' |')
                                continue
                            extra_row = [op_id_val, burst]
                        elif perf_code == 'PERF-012':
                            # If no matched operation and no explicit hint, expand into one row per operation for this service
                            if not matched_op and not op_hint:
                                for oid, op in sorted(op_lookup.items()):
                                    oid_disp = display_operation(service, oid) if oid else ''
                                    sustained_val = str(op.get('sustained_tps_target',''))
                                    row = base_row + [oid_disp, sustained_val] + [it.get('rationale','')]
                                    dmd.append('| ' + ' | '.join(row) + ' |')
                                continue
                            extra_row = [op_id_val, sustained]
                        elif perf_code == 'PERF-013':
                            # If no matched operation and no explicit hint, expand into one row per operation for this service
                            if not matched_op and not op_hint:
                                for oid, op in sorted(op_lookup.items()):
                                    oid_disp = display_operation(service, oid) if oid else ''
                                    payload_val = str(op.get('max_request_payload_bytes',''))
                                    row = base_row + [oid_disp, payload_val] + [it.get('rationale','')]
                                    dmd.append('| ' + ' | '.join(row) + ' |')
                                # Continue to next control item
                                continue
                            extra_row = [op_id_val, payload]
                    row = base_row + extra_row + [it.get('rationale','')]
                    dmd.append('| ' + ' | '.join(row) + ' |')
                _append_blank_line(dmd)
            dom_file.write_text('\n'.join(dmd), encoding='utf-8')


def write_service_summary(service_map: Dict[str, List[Dict[str, str]]]) -> None:
    SERVICE_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    service_names = load_service_display_names()
    def display_service(s: str) -> str:
        return service_names.get(s, s)
    lines.append("# FtRS NFR – By Service")
    lines.append("")
    lines.append("This page is auto-generated; do not hand-edit.")
    lines.append("")
    # Add concise definitions near the top for clarity
    lines.append("## Definitions")
    lines.append("")
    lines.append("- Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.")
    lines.append("- Operation: performance-specific expectation for an endpoint or job. Tied to a service and operation_id; sets p50/p95 latency, absolute max, burst/sustained TPS, payload limits, status, rationale, and stories.")
    lines.append("")
    lines.append("## Service Index")
    lines.append("")
    lines.append("| Service | Page |")
    lines.append("|---------|------|")
    for service in sorted(service_map.keys(), key=lambda s: display_service(s).lower()):
        rel = f"nfr-by-service/{service}/index.md"
        disp = display_service(service)
        lines.append(f"| {disp} | [{disp}]({rel}) |")
    lines.append("")
    SERVICE_SUMMARY.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    service_map = collect_service_map()
    write_service_pages(service_map)
    write_service_summary(service_map)
    print(f"Generated {len(service_map)} service pages in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
