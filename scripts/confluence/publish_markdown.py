#!/usr/bin/env python3
from __future__ import annotations
import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

import requests
import re

try:
    import markdown as mdlib  # type: ignore
    MD_AVAILABLE = True
except Exception:
    MD_AVAILABLE = False


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def wrap_markdown_macro(markdown_text: str) -> str:
    return (
        '<ac:structured-macro ac:name="markdown">'
        '<ac:plain-text-body><![CDATA['
        + markdown_text +
        ']]></ac:plain-text-body>'
        '</ac:structured-macro>'
    )


def jira_issue_macro(key: str, server_id: Optional[str] = None, server_name: Optional[str] = None) -> str:
    # Prefer key-based macro; optionally include serverId or server name
    params = [f'<ac:parameter ac:name="key">{key}</ac:parameter>']
    if server_id:
        params.append(f'<ac:parameter ac:name="serverId">{server_id}</ac:parameter>')
    elif server_name:
        params.append(f'<ac:parameter ac:name="server">{server_name}</ac:parameter>')
    return '<ac:structured-macro ac:name="jira">' + ''.join(params) + '</ac:structured-macro>'


def markdown_to_storage(markdown_text: str, use_jira_macro: bool = False, jira_server_id: Optional[str] = None, jira_server_name: Optional[str] = None) -> str:
    # Convert Markdown to HTML (Confluence storage accepts XHTML/HTML subset)
    if not MD_AVAILABLE:
        raise RuntimeError("Python-Markdown not installed; cannot convert Markdown to Confluence storage. Install 'markdown' or use --use-markdown-macro explicitly.")
    html = mdlib.markdown(markdown_text, extensions=["tables", "fenced_code"])  # type: ignore
    # Replace Jira issue links with Jira macro if requested
    if use_jira_macro:
        jira_re = re.compile(r'<a\s+href=["\"](?:https?://[^\"\']+/browse/)?(FTRS-\d+)["\"][^>]*>.*?</a>', re.IGNORECASE)
        def _repl(m: re.Match) -> str:
            key = m.group(1)
            return jira_issue_macro(key, server_id=jira_server_id, server_name=jira_server_name)
        html = jira_re.sub(_repl, html)
    return html


def confluence_page_link(title: str, space: Optional[str] = None, link_text: Optional[str] = None, anchor: Optional[str] = None) -> str:
    # Return a Confluence storage link to a page by content title, with optional space and anchor
    safe_title = (title or "").replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    page = f'<ri:page ri:content-title="{safe_title}"' + (f' ri:space-key="{space}"' if space else '') + ' />'
    parts = ['<ac:link>', page]
    if link_text is not None and link_text != '':
        parts.append('<ac:link-body><![CDATA[' + link_text + ']]></ac:link-body>')
    if anchor:
        parts.append(f'<ac:anchor>{anchor}</ac:anchor>')
    parts.append('</ac:link>')
    return ''.join(parts)


def rewrite_service_index_links_to_page_links(html: str, map_folder_to_title) -> str:
    """Rewrite anchors pointing at nfr-by-service/<folder>/index.md to Confluence page links.

    This ensures the Service Index links point to the service pages (which are titled by service name)
    rather than raw markdown file paths.
    """
    # Match <a href="nfr-by-service/<folder>/index.md">...</a>
    re_href = re.compile(r'<a\s+href=["\'](?:\.?/)?nfr-by-service/([^/]+)/index\.md["\'][^>]*>.*?</a>', re.IGNORECASE)
    def _repl(m: re.Match) -> str:
        folder = m.group(1)
        title = map_folder_to_title(folder)
        return confluence_page_link(title)
    return re_href.sub(_repl, html)


def rewrite_explanations_links_to_page_link(html: str, space: Optional[str] = None, base_url: Optional[str] = None, page_id: Optional[str] = None) -> str:
    """Rewrite anchors pointing at ../explanations.md (or ../../explanations.md) to a Confluence page link.

    Preserves fragment identifiers by emitting an <ac:anchor> targeting the Explanations page.
    """
    re_href = re.compile(r'<a\s+href=["\'](?:\.\./){1,2}explanations\.md(#[^"\']*)?["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
    def _repl(m: re.Match) -> str:
        frag = (m.group(1) or "").lstrip('#')
        text = m.group(2) or ''
        if frag:
            raw = frag.strip()
            if raw.lower().startswith('explanations-'):
                raw = raw[len('explanations-'):]
            code = raw.upper()
            anchor = f"Explanations-{code}"
            if base_url and space and page_id:
                url = f"{base_url}/spaces/{space}/pages/{page_id}/Explanations#{anchor}"
                return f'<a href="{url}">{text}</a>'
            return confluence_page_link("Explanations", space=space, link_text=text, anchor=anchor)
        if base_url and space and page_id:
            url = f"{base_url}/spaces/{space}/pages/{page_id}/Explanations"
            return f'<a href="{url}">{text}</a>'
        return confluence_page_link("Explanations", space=space, link_text=text)
    return re_href.sub(_repl, html)


def inject_code_anchors_for_explanations(storage_html: str) -> str:
    """Insert explicit anchor macros before each code heading (e.g., <h3>INT-003</h3>).

    This guarantees stable anchors like 'int-003' regardless of Confluence's auto-generated IDs.
    """
    # Match H3 headings that look like NFR codes, e.g., INT-003, GOV-010, OBS-001
    re_h3_code = re.compile(r'(<h3>)([A-Z]+-[0-9]{3})(</h3>)')
    def _repl(m: re.Match) -> str:
        code = m.group(2)
        anchors = [code, f"Explanations-{code}"]
        macros = []
        for a in anchors:
            macros.append(
                '<ac:structured-macro ac:name="anchor">'
                f'<ac:parameter ac:name="anchor">{a}</ac:parameter>'
                '</ac:structured-macro>'
            )
        return ''.join(macros) + m.group(1) + code + m.group(3)
    return re_h3_code.sub(_repl, storage_html)


def _sanitize_title_for_anchor(title: str) -> str:
    # Confluence heading anchors often squash spaces; retain punctuation/dashes to mirror UI
    return (title or "").replace(" ", "")


def inject_code_anchors_for_page(storage_html: str, page_title: str) -> str:
    """Insert anchors for NFR code headings across any page.

        Adds two anchors per code:
            - lowercase: int-002
            - uppercase: INT-002
    """
    re_h3_code = re.compile(r'(<h3>)([A-Z]+-[0-9]{3})(</h3>)')
    def _repl(m: re.Match) -> str:
        code_upper = m.group(2)
        code_lower = code_upper.lower()
        # Only simple, macro-safe anchors to avoid REST 400 errors from invalid names
        anchors = [code_lower, code_upper]
        parts = []
        for a in anchors:
            parts.append(
                '<ac:structured-macro ac:name="anchor">'
                f'<ac:parameter ac:name="anchor">{a}</ac:parameter>'
                '</ac:structured-macro>'
            )
        return ''.join(parts) + m.group(1) + code_upper + m.group(3)
    return re_h3_code.sub(_repl, storage_html)


def children_display_macro() -> str:
    # Storage macro that renders links to all child pages of the current page
    return (
        '<ac:structured-macro ac:name="children">'
        '<ac:parameter ac:name="sort">title</ac:parameter>'
        '<ac:parameter ac:name="reverse">false</ac:parameter>'
        '<ac:parameter ac:name="style">h4</ac:parameter>'
        '<ac:parameter ac:name="excerpt">none</ac:parameter>'
        '<ac:parameter ac:name="children">all</ac:parameter>'
        '<ac:parameter ac:name="type">page</ac:parameter>'
        '</ac:structured-macro>'
    )


def basic_auth_header(user: str, token: str) -> Dict[str, str]:
    raw = f"{user}:{token}".encode("utf-8")
    return {"Authorization": "Basic " + base64.b64encode(raw).decode("ascii")}


def bearer_auth_header(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def api_get_page(base_url: str, space: str, title: str, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    url = f"{base_url}/rest/api/content"
    params = {"spaceKey": space, "title": title, "expand": "version"}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    return results[0] if results else None

def api_get_page_in_ancestor(base_url: str, space: str, title: str, ancestor_id: str, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    # Prefer finding a page with matching title under the specified ancestor
    # Use CQL to scope by space, title, and ancestor
    cql = f'title = "{title}" AND space = "{space}" AND ancestor = {ancestor_id}'
    url = f"{base_url}/rest/api/content/search"
    params = {"cql": cql, "expand": "version"}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    return results[0] if results else None

def api_get_direct_parent_id(base_url: str, page_id: str, headers: Dict[str, str]) -> Optional[str]:
    url = f"{base_url}/rest/api/content/{page_id}"
    params = {"expand": "ancestors"}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    ancestors = data.get("ancestors", []) or []
    if not ancestors:
        return None
    return str(ancestors[-1].get("id")) if ancestors else None

def api_move_page(base_url: str, page_id: str, target_parent_id: str, headers: Dict[str, str]) -> None:
    # Move the page to be a child of target_parent_id by appending under it
    # Confluence REST (Server/DC & Cloud): POST /rest/api/content/{id}/move/append?targetId={target}
    url = f"{base_url}/rest/api/content/{page_id}/move/append"
    r = requests.post(url, headers=headers, params={"targetId": str(target_parent_id)}, timeout=60)
    r.raise_for_status()


def api_create_page(base_url: str, space: str, title: str, parent_id: Optional[str], storage_body: str, headers: Dict[str, str]) -> Dict[str, Any]:
    url = f"{base_url}/rest/api/content"
    payload: Dict[str, Any] = {
        "type": "page",
        "title": title,
        "space": {"key": space},
        "body": {
            "storage": {
                "value": storage_body,
                "representation": "storage",
            }
        },
    }
    if parent_id:
        payload["ancestors"] = [{"id": str(parent_id)}]
    r = requests.post(url, headers={**headers, "Content-Type": "application/json"}, data=json.dumps(payload), timeout=60)
    r.raise_for_status()
    return r.json()


def api_update_page(base_url: str, page_id: str, title: str, storage_body: str, current_version: int, headers: Dict[str, str], parent_id: Optional[str] = None) -> Dict[str, Any]:
    url = f"{base_url}/rest/api/content/{page_id}"
    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "version": {"number": current_version + 1},
        "body": {
            "storage": {
                "value": storage_body,
                "representation": "storage",
            }
        },
        # Minor edit reduces notifications noise
        "minorEdit": True,
    }
    if parent_id:
        payload["ancestors"] = [{"id": str(parent_id)}]
    r = requests.put(url, headers={**headers, "Content-Type": "application/json"}, data=json.dumps(payload), timeout=60)
    r.raise_for_status()
    return r.json()


def api_delete_page(base_url: str, page_id: str, headers: Dict[str, str]) -> None:
    url = f"{base_url}/rest/api/content/{page_id}"
    r = requests.delete(url, headers=headers, timeout=30)
    r.raise_for_status()


def publish_one(base_url: str, auth_mode: str, user: Optional[str], token: str, space: str, title: str, md_text: str, parent_id: Optional[str], storage_override: Optional[str] = None, prefer_storage: bool = True, jira_macro: bool = False, jira_server_id: Optional[str] = None, jira_server_name: Optional[str] = None) -> str:
    headers = bearer_auth_header(token) if auth_mode == "bearer" else basic_auth_header(user or "", token)
    if storage_override is not None:
        storage = storage_override
    else:
        storage = markdown_to_storage(md_text, use_jira_macro=jira_macro, jira_server_id=jira_server_id, jira_server_name=jira_server_name) if prefer_storage else wrap_markdown_macro(md_text)
    existing = None
    if parent_id:
        # First, try to find the page under the requested ancestor
        existing = api_get_page_in_ancestor(base_url, space, title, str(parent_id), headers)
    if not existing:
        # Fallback to any page with same title in space
        existing = api_get_page(base_url, space, title, headers)
    if existing:
        page_id = existing["id"]
        cur_version = int(existing.get("version", {}).get("number", 1))
        # Do NOT change ancestors during update; only update content
        api_update_page(base_url, page_id, title, storage, cur_version, headers, parent_id=None)
        return page_id
    # If no existing page found under the specified ancestor, do not search space-wide or move pages
    # The caller may decide to create a new page if allowed and safe
    raise FileNotFoundError(f"Page titled '{title}' not found under ancestor {parent_id}")


def _title_case(s: str) -> str:
    return " ".join(w.capitalize() for w in s.replace('-', ' ').replace('_', ' ').split())

def derive_title_from_path(path: Path) -> str:
    p = path.as_posix()
    parts = p.split('/')
    # Per-service domain page: docs/nfrs/nfr-by-service/<service>/<domain>.md
    if 'nfr-by-service' in parts:
        try:
            idx = parts.index('nfr-by-service')
            svc = parts[idx+1]
            dom = Path(parts[-1]).stem
            dom_tc = _title_case(dom)
            suffix = "NFRs & Operations" if dom_tc == "Performance" else "NFRs & Controls"
            return f"{_title_case(svc)} – {dom_tc} {suffix}"
        except Exception:
            pass
    # Domain page: docs/nfrs/nfr-by-domain/<domain>.md
    if '/nfr-by-domain/' in p:
        dom = _title_case(Path(p).stem)
        # Confluence titles include suffixes to avoid collision
        # Most domains use "NFRs & Controls"; Performance uses "NFRs & Operations"
        if dom == "Performance":
            return f"{dom} NFRs & Operations"
        else:
            return f"{dom} NFRs & Controls"
    # Fallback: file stem
    return _title_case(path.stem)


def main() -> None:
    p = argparse.ArgumentParser(description="Publish Markdown files to Confluence using the Markdown macro")
    p.add_argument("files", nargs="+", help="Markdown files to publish")
    p.add_argument("--base-url", required=False, default=os.getenv("CONFLUENCE_BASE_URL", ""), help="Base URL, e.g. https://your-domain.atlassian.net/wiki")
    p.add_argument("--space", required=False, default=os.getenv("CONFLUENCE_SPACE", ""), help="Space key")
    p.add_argument("--parent-id", required=False, default=os.getenv("CONFLUENCE_PARENT_ID", ""), help="Legacy: single parent page ID for all (optional)")
    p.add_argument("--top-parent-id", required=False, default=os.getenv("CONFLUENCE_TOP_PARENT_ID", ""), help="Top-level parent page ID (optional)")
    p.add_argument("--domain-parent-id", required=False, default=os.getenv("CONFLUENCE_DOMAIN_PARENT_ID", ""), help="Parent page ID for NFRs by Domain (recommended)")
    p.add_argument("--service-parent-id", required=False, default=os.getenv("CONFLUENCE_SERVICE_PARENT_ID", ""), help="Parent page ID for NFRs by Service (optional)")
    p.add_argument("--allow-create-if-missing", action="store_true", help="Create pages only under the resolved parent if not found. No fallback or moves.")
    p.add_argument("--title", required=False, help="Explicit title to use when a single file is provided")
    p.add_argument("--auth", choices=["basic", "bearer"], default=os.getenv("CONFLUENCE_AUTH", "basic"), help="Auth mode: basic (email+token) or bearer (PAT)")
    p.add_argument("--user", required=False, default=os.getenv("CONFLUENCE_USER", ""), help="Username/email (basic auth)")
    p.add_argument("--token", required=False, default=os.getenv("CONFLUENCE_TOKEN", ""), help="API token or PAT")
    p.add_argument("--dry-run", action="store_true", help="Non-destructive: report intended actions without creating or updating any pages")
    p.add_argument("--use-markdown-macro", action="store_true", help="Force using the Markdown macro instead of converting to storage format")
    p.add_argument("--jira-macro", action="store_true", default=os.getenv("CONFLUENCE_USE_JIRA_MACRO", "false").lower() in {"1", "true", "yes"}, help="Convert Jira issue links to Jira macros where possible")
    p.add_argument("--jira-server-id", default=os.getenv("CONFLUENCE_JIRA_SERVER_ID", ""), help="Confluence Application Link serverId for Jira (optional)")
    p.add_argument("--jira-server-name", default=os.getenv("CONFLUENCE_JIRA_SERVER", ""), help="Confluence Application Link server name for Jira (optional)")
    p.add_argument("--prune-missing", action="store_true", help="Delete auto-generated pages in Confluence that are not present in local inputs under the configured parent(s)")
    p.add_argument("--prune-scope", choices=["domain","service","all"], default="all", help="Limit prune to a branch: domain, service, or all")

    args = p.parse_args()
    if not args.base_url or not args.space or not args.token or (args.auth == "basic" and not args.user):
        print("Missing required auth/base/space arguments. Set env vars or pass flags.", file=sys.stderr)
        p.print_help(sys.stderr)
        sys.exit(2)

    base_url = args.base_url.rstrip("/")

    # Resolve category parents
    category_domain_title = "NFRs by Domain"
    category_service_title = "NFRs by Service"
    headers = bearer_auth_header(args.token) if args.auth == "bearer" else basic_auth_header(args.user or "", args.token)
    domain_parent_id = args.domain_parent_id or None
    service_parent_id = args.service_parent_id or None
    if (not domain_parent_id or not service_parent_id) and args.top_parent_id:
        top_id = str(args.top_parent_id)
        # list children and find by title; DO NOT create missing categories automatically
        url = f"{base_url}/rest/api/content/{top_id}/child/page"
        r = requests.get(url, headers=headers, params={"limit": 200}, timeout=30)
        r.raise_for_status()
        kids = r.json().get("results", [])
        def _get_child_id(title: str) -> Optional[str]:
            for k in kids:
                if k.get("title") == title:
                    return str(k.get("id"))
            return None
        did = _get_child_id(category_domain_title)
        sid = _get_child_id(category_service_title)
        if not domain_parent_id:
            domain_parent_id = did
        if not service_parent_id:
            service_parent_id = sid

    # Cache of service pages under the service category parent, map title->id
    service_children: Dict[str, str] = {}
    if service_parent_id:
        url = f"{base_url}/rest/api/content/{service_parent_id}/child/page"
        r = requests.get(url, headers=headers, params={"limit": 500}, timeout=30)
        r.raise_for_status()
        for item in r.json().get("results", []):
            t = item.get("title") or ""
            service_children[t] = str(item.get("id"))

    # Resolve Explanations page ID (space-wide)
    explanations_page = api_get_page(base_url, args.space, "Explanations", headers)
    explanations_page_id = str(explanations_page.get("id")) if explanations_page else None

    def map_service_folder_to_title(folder: str) -> str:
        key = folder.strip().lower()
        mapping = {
            "crud-apis": "CRUD APIs",
            "data-migration": "Data Migration",
            "dos-ingestion-api": "DoS Ingress API",
            "dos-search": "DoS Search",
            "etl-ods": "ETL - ODS",
            "read-only-viewer": "Read-only Viewer",
        }
        return mapping.get(key, _title_case(folder))

    last_id = None
    for f in args.files:
        path = Path(f)
        if not path.exists():
            print(f"Skipping missing file: {path}", file=sys.stderr)
            continue
        md = read_text(path)
        title = args.title if (args.title and len(args.files) == 1) else derive_title_from_path(path)
        # choose parent per file category
        parent_for_file: Optional[str] = None
        pstr = path.as_posix()
        # Special-case: domain index should update the category page itself
        is_domain_index = pstr.endswith('docs/nfrs/nfr-by-domain.md') or path.name.lower() == 'nfr-by-domain.md'
        # Special-case: service top index should update the category page itself
        is_service_top_index = pstr.endswith('docs/nfrs/nfr-by-service.md') or path.name.lower() == 'nfr-by-service.md'
        if is_domain_index:
            # Update the category page titled "NFRs by Domain"; search space-wide to avoid ancestor mismatch
            category_domain_title = "NFRs by Domain"
            if not args.title:
                title = category_domain_title
            parent_for_file = None
        elif is_service_top_index:
            # Update the category page titled "NFRs by Service"; search space-wide to avoid ancestor mismatch
            category_service_title = "NFRs by Service"
            if not args.title:
                title = category_service_title
            parent_for_file = None
        else:
            if '/nfr-by-domain/' in pstr:
                parent_for_file = (domain_parent_id or args.parent_id or None)
            elif '/nfr-by-service/' in pstr:
                # Resolve to the specific service page under the service category
                try:
                    parts2 = pstr.split('/')
                    idx2 = parts2.index('nfrs')  # docs/nfrs/nfr-by-service/<service>/...
                    svc_folder = parts2[idx2+2]
                except Exception:
                    svc_folder = parts2[parts2.index('nfr-by-service')+1] if 'nfr-by-service' in parts2 else ''
                svc_title = map_service_folder_to_title(svc_folder)
                # Special-case: index.md should update the service page itself (top-level content)
                is_index = path.name.lower() == 'index.md'
                if is_index:
                    # For updates, search under the service category parent and target the service page title
                    if not args.title:
                        title = svc_title
                    parent_for_file = (service_parent_id or args.parent_id or None)
                else:
                    parent_for_file = service_children.get(svc_title, None)
            else:
                parent_for_file = (args.parent_id or domain_parent_id or service_parent_id or None)
        # Dry-run: only report actions
        if args.dry_run:
            existing_under_parent = None
            if parent_for_file:
                existing_under_parent = api_get_page_in_ancestor(base_url, args.space, title, str(parent_for_file), headers)
            if existing_under_parent:
                pid = existing_under_parent.get("id")
                print(f"Would update '{title}' under parent {parent_for_file} (page {pid}) from {path}")
                last_id = pid
            else:
                if parent_for_file:
                    # Report intended creation under the resolved service page
                    existing_anywhere = api_get_page(base_url, args.space, title, headers)
                    if existing_anywhere:
                        print(f"Would NOT create '{title}' (duplicate exists elsewhere in space). Provide explicit parent or rename.")
                    else:
                        print(f"Would create '{title}' under parent {parent_for_file} from {path}")
                        last_id = "pending-create"
                else:
                    print(f"Not found under expected parent for '{title}'. Would skip without changes.")
            continue

        # Live: perform safe publish
        try:
            # Build storage body without adding Children macro (links are now explicit)
            storage_override = None
            is_service_index = ('/nfr-by-service/' in pstr and path.name.lower() == 'index.md')
            is_explanations_page = pstr.endswith('docs/nfrs/explanations.md') or path.name.lower() == 'explanations.md'
            if is_service_index:
                storage_override = markdown_to_storage(md, use_jira_macro=args.jira_macro, jira_server_id=(args.jira_server_id or None), jira_server_name=(args.jira_server_name or None)) if not args.use_markdown_macro else wrap_markdown_macro(md)
            if is_domain_index:
                storage_override = markdown_to_storage(md, use_jira_macro=args.jira_macro, jira_server_id=(args.jira_server_id or None), jira_server_name=(args.jira_server_name or None)) if not args.use_markdown_macro else wrap_markdown_macro(md)
            if is_service_top_index:
                # Convert markdown and rewrite links to Confluence page links
                if not args.use_markdown_macro:
                    body = markdown_to_storage(md, use_jira_macro=args.jira_macro, jira_server_id=(args.jira_server_id or None), jira_server_name=(args.jira_server_name or None))
                    body = rewrite_service_index_links_to_page_links(body, map_service_folder_to_title)
                else:
                    body = wrap_markdown_macro(md)
                storage_override = body
            # Apply explanation link rewriting when we already built storage
            if storage_override is not None and not args.use_markdown_macro:
                storage_override = rewrite_explanations_links_to_page_link(storage_override, space=args.space, base_url=base_url, page_id=explanations_page_id)
                # inject generic anchors on any page with code headings
                storage_override = inject_code_anchors_for_page(storage_override, title)
            # If publishing the Explanations page, inject explicit anchor macros for each code
            if storage_override is not None and not args.use_markdown_macro and is_explanations_page:
                storage_override = inject_code_anchors_for_explanations(storage_override)

            # If this is the domain index and we resolved the category page id, update it directly by ID
            if is_domain_index and domain_parent_id:
                # Fetch current version and title for the category page
                url = f"{base_url}/rest/api/content/{domain_parent_id}"
                r = requests.get(url, headers=headers, params={"expand": "version"}, timeout=30)
                r.raise_for_status()
                info = r.json()
                cur_v = int((info.get("version") or {}).get("number", 1))
                cur_title = info.get("title") or title
                body = storage_override if storage_override is not None else (markdown_to_storage(md, use_jira_macro=args.jira_macro, jira_server_id=(args.jira_server_id or None), jira_server_name=(args.jira_server_name or None)) if not args.use_markdown_macro else wrap_markdown_macro(md))
                if not args.use_markdown_macro and is_explanations_page:
                    body = inject_code_anchors_for_explanations(body)
                if not args.use_markdown_macro:
                    body = inject_code_anchors_for_page(body, cur_title)
                api_update_page(base_url, str(domain_parent_id), cur_title, body, cur_v, headers, parent_id=None)
                print(f"Published {path} -> page {domain_parent_id} ('{cur_title}')")
                last_id = str(domain_parent_id)
                continue
            # If this is the service top index and we resolved the category page id, update it directly by ID
            if is_service_top_index and service_parent_id:
                url = f"{base_url}/rest/api/content/{service_parent_id}"
                r = requests.get(url, headers=headers, params={"expand": "version"}, timeout=30)
                r.raise_for_status()
                info = r.json()
                cur_v = int((info.get("version") or {}).get("number", 1))
                cur_title = info.get("title") or title
                body = storage_override if storage_override is not None else (markdown_to_storage(md, use_jira_macro=args.jira_macro, jira_server_id=(args.jira_server_id or None), jira_server_name=(args.jira_server_name or None)) if not args.use_markdown_macro else wrap_markdown_macro(md))
                if not args.use_markdown_macro and is_explanations_page:
                    body = inject_code_anchors_for_explanations(body)
                if not args.use_markdown_macro:
                    body = inject_code_anchors_for_page(body, cur_title)
                api_update_page(base_url, str(service_parent_id), cur_title, body, cur_v, headers, parent_id=None)
                print(f"Published {path} -> page {service_parent_id} ('{cur_title}')")
                last_id = str(service_parent_id)
                continue
            # For non-macro, convert here to enable explanation link rewriting
            storage_override_general = None
            if not args.use_markdown_macro:
                body = markdown_to_storage(md, use_jira_macro=args.jira_macro, jira_server_id=(args.jira_server_id or None), jira_server_name=(args.jira_server_name or None))
                body = rewrite_explanations_links_to_page_link(body, space=args.space, base_url=base_url, page_id=explanations_page_id)
                if is_explanations_page:
                    body = inject_code_anchors_for_explanations(body)
                body = inject_code_anchors_for_page(body, title)
                storage_override_general = body
            page_id = publish_one(
                base_url,
                args.auth,
                args.user,
                args.token,
                args.space,
                title,
                md,
                parent_for_file,
                storage_override=(storage_override if storage_override is not None else storage_override_general),
                prefer_storage=(not args.use_markdown_macro),
                jira_macro=args.jira_macro,
                jira_server_id=(args.jira_server_id or None),
                jira_server_name=(args.jira_server_name or None),
            )
            print(f"Published {path} -> page {page_id} ('{title}')")
            last_id = page_id
        except FileNotFoundError:
            if args.allow_create_if_missing and parent_for_file:
                existing_anywhere = api_get_page(base_url, args.space, title, headers)
                if existing_anywhere:
                    print(f"Skip create for {title}: a page with this title exists elsewhere in the space. Provide explicit parent IDs or rename.", file=sys.stderr)
                    continue
                storage_override = None
                is_service_index = ('/nfr-by-service/' in pstr and path.name.lower() == 'index.md')
                if is_service_index:
                    storage_override = markdown_to_storage(md, use_jira_macro=args.jira_macro, jira_server_id=(args.jira_server_id or None), jira_server_name=(args.jira_server_name or None)) if not args.use_markdown_macro else wrap_markdown_macro(md)
                if is_domain_index:
                    storage_override = markdown_to_storage(md, use_jira_macro=args.jira_macro, jira_server_id=(args.jira_server_id or None), jira_server_name=(args.jira_server_name or None)) if not args.use_markdown_macro else wrap_markdown_macro(md)
                if is_service_top_index:
                    if not args.use_markdown_macro:
                        body = markdown_to_storage(md, use_jira_macro=args.jira_macro, jira_server_id=(args.jira_server_id or None), jira_server_name=(args.jira_server_name or None))
                        body = rewrite_service_index_links_to_page_links(body, map_service_folder_to_title)
                    else:
                        body = wrap_markdown_macro(md)
                    storage_override = body
                # If not using markdown macro, do not fallback silently – raise if conversion unavailable
                body = storage_override if storage_override is not None else (markdown_to_storage(md, use_jira_macro=args.jira_macro, jira_server_id=(args.jira_server_id or None), jira_server_name=(args.jira_server_name or None)) if not args.use_markdown_macro else wrap_markdown_macro(md))
                if not args.use_markdown_macro and is_explanations_page:
                    body = inject_code_anchors_for_explanations(body)
                if not args.use_markdown_macro:
                    body = inject_code_anchors_for_page(body, title)
                created = api_create_page(base_url, args.space, title, parent_for_file, body, headers)
                print(f"Created {path} -> page {created.get('id')} ('{title}')")
                last_id = str(created.get('id'))
            else:
                print(f"Not found under expected parent for '{title}'. Skipping without changes.", file=sys.stderr)
                continue

    if last_id is None:
        # Do not exit early; we may still run prune below
        pass

    # Optional prune step: remove extra auto-generated pages not represented in local files
    if args.prune_missing:
        AUTO_MARKER = "This page is auto-generated; do not hand-edit."

        def _get_body(page_id: str) -> str:
            url = f"{base_url}/rest/api/content/{page_id}"
            r = requests.get(url, headers=headers, params={"expand": "body.storage"}, timeout=30)
            r.raise_for_status()
            data = r.json()
            return (((data.get("body") or {}).get("storage") or {}).get("value") or "")

        # Build expected title sets from the provided file list
        expected_domain_titles: set[str] = set()
        expected_service_titles: set[str] = set()
        expected_service_children: Dict[str, set[str]] = {}

        for f in args.files:
            pth = Path(f)
            pstr = pth.as_posix()
            if "/nfr-by-domain/" in pstr and pth.name.lower().endswith(".md"):
                # Skip the top index file
                if pth.name.lower() != "nfr-by-domain.md":
                    expected_domain_titles.add(derive_title_from_path(pth))
            if "/nfr-by-service/" in pstr and pth.name.lower().endswith(".md"):
                parts2 = pstr.split('/')
                try:
                    idx2 = parts2.index('nfrs')
                    svc_folder = parts2[idx2+2]
                except Exception:
                    svc_folder = parts2[parts2.index('nfr-by-service')+1] if 'nfr-by-service' in parts2 else ''
                svc_title = map_service_folder_to_title(svc_folder)
                if pth.name.lower() == 'index.md':
                    expected_service_titles.add(svc_title)
                else:
                    expected_service_children.setdefault(svc_title, set()).add(derive_title_from_path(pth))

        def _prune_under_parent(parent_id: str, expected_titles: set[str]) -> None:
            url = f"{base_url}/rest/api/content/{parent_id}/child/page"
            r = requests.get(url, headers=headers, params={"limit": 500}, timeout=30)
            r.raise_for_status()
            for item in r.json().get("results", []):
                pid = str(item.get("id"))
                title = item.get("title") or ""
                if title in expected_titles:
                    continue
                body = _get_body(pid)
                if AUTO_MARKER in body:
                    msg = f"Prune: deleting page {pid} ('{title}') under parent {parent_id}"
                    if args.dry_run:
                        print(f"Would {msg}")
                    else:
                        api_delete_page(base_url, pid, headers)
                        print(msg)

        def _prune_service_children() -> None:
            if not service_parent_id:
                return
            # For each service page under the service category, prune its children against expected list
            url = f"{base_url}/rest/api/content/{service_parent_id}/child/page"
            r = requests.get(url, headers=headers, params={"limit": 500}, timeout=30)
            r.raise_for_status()
            for svc_item in r.json().get("results", []):
                svc_title = svc_item.get("title") or ""
                svc_id = str(svc_item.get("id"))
                expected = expected_service_children.get(svc_title, set())
                # List children of the service page
                url2 = f"{base_url}/rest/api/content/{svc_id}/child/page"
                r2 = requests.get(url2, headers=headers, params={"limit": 500}, timeout=30)
                r2.raise_for_status()
                for child in r2.json().get("results", []):
                    cid = str(child.get("id"))
                    ctitle = child.get("title") or ""
                    if ctitle in expected:
                        continue
                    body = _get_body(cid)
                    if AUTO_MARKER in body:
                        msg = f"Prune: deleting page {cid} ('{ctitle}') under service '{svc_title}'"
                        if args.dry_run:
                            print(f"Would {msg}")
                        else:
                            api_delete_page(base_url, cid, headers)
                            print(msg)

        scope = args.prune_scope
        if scope in ("all", "domain") and domain_parent_id:
            _prune_under_parent(str(domain_parent_id), expected_domain_titles)
        if scope in ("all", "service") and service_parent_id:
            _prune_under_parent(str(service_parent_id), expected_service_titles)
            _prune_service_children()


if __name__ == "__main__":
    main()
