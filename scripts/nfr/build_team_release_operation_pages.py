#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any

try:
    import yaml  # type: ignore
    YAML_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - environment dependency
    YAML_AVAILABLE = False

ROOT = Path(__file__).resolve().parents[2]
DOMAIN_NFRS_DIR = ROOT / "requirements" / "nfrs"
DOCS_DIR = ROOT / "docs" / "nfrs"
TEAM_INDEX = DOCS_DIR / "nfr-by-team.md"
TEAM_DIR = DOCS_DIR / "nfr-by-team"
RELEASE_INDEX = DOCS_DIR / "nfr-by-release.md"
RELEASE_DIR = DOCS_DIR / "nfr-by-release"
OP_INDEX = DOCS_DIR / "nfr-by-operation.md"
OP_DIR = DOCS_DIR / "nfr-by-operation"


@dataclass
class ReleaseInfo:
    id: str
    operations: List[str] = field(default_factory=list)
    overall_status: str | None = None
    team_status: Dict[str, str] = field(default_factory=dict)


@dataclass
class Nfr:
    domain: str
    code: str
    requirement: str
    explanation: str
    stories: List[str]
    services: List[str]
    teams: List[str]
    operations: List[str]  # operation_id only
    releases: List[ReleaseInfo]


def load_domain_yaml(domain: str) -> dict:
    if not YAML_AVAILABLE:
        return {}
    path = DOMAIN_NFRS_DIR / domain / "nfrs.yaml"
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def load_all_nfrs() -> List[Nfr]:
    nfrs: List[Nfr] = []
    if not DOMAIN_NFRS_DIR.exists():
        return nfrs

    for domain_dir in sorted(p for p in DOMAIN_NFRS_DIR.iterdir() if p.is_dir()):
        domain = domain_dir.name
        data = load_domain_yaml(domain)
        for raw in data.get("nfrs", []) or []:
            code = str(raw.get("code", "")).strip()
            if not code:
                continue
            requirement = str(raw.get("requirement", "")).strip()
            explanation = str(raw.get("explanation") or "").strip()
            stories = [str(s) for s in (raw.get("stories") or [])]
            services = [str(s) for s in (raw.get("services") or [])]
            teams = [str(t) for t in (raw.get("teams") or [])]

            ops: List[str] = []
            for op in raw.get("operations", []) or []:
                op_id = op.get("operation_id")
                if isinstance(op_id, str) and op_id.strip():
                    ops.append(op_id.strip())

            rels: List[ReleaseInfo] = []
            for r in raw.get("releases", []) or []:
                rel_id = r.get("id")
                if not isinstance(rel_id, str) or not rel_id.strip():
                    continue
                rel_ops: List[str] = []
                for o in r.get("operations", []) or []:
                    if isinstance(o, str) and o.strip():
                        rel_ops.append(o.strip())
                overall_status = r.get("overall_status")
                if isinstance(overall_status, str):
                    overall_status = overall_status.strip() or None
                team_status: Dict[str, str] = {}
                ts_raw: Any = r.get("team_status")
                if isinstance(ts_raw, dict):
                    for k, v in ts_raw.items():
                        if isinstance(k, str) and isinstance(v, str):
                            if k.strip() and v.strip():
                                team_status[k.strip()] = v.strip()
                rels.append(
                    ReleaseInfo(
                        id=rel_id.strip(),
                        operations=rel_ops,
                        overall_status=overall_status,
                        team_status=team_status,
                    )
                )

            nfrs.append(
                Nfr(
                    domain=domain.capitalize(),
                    code=code,
                    requirement=requirement,
                    explanation=explanation,
                    stories=stories,
                    services=services,
                    teams=teams,
                    operations=ops,
                    releases=rels,
                )
            )

    return nfrs


def ensure_dirs() -> None:
    TEAM_DIR.mkdir(parents=True, exist_ok=True)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    OP_DIR.mkdir(parents=True, exist_ok=True)


def build_team_views(nfrs: List[Nfr]) -> None:
    team_to_nfrs: Dict[str, List[Nfr]] = defaultdict(list)

    for n in nfrs:
        # Direct teams on the NFR
        for team in n.teams:
            team_to_nfrs[team].append(n)
        # Teams referenced in any release team_status
        for rel in n.releases:
            for team in rel.team_status.keys():
                team_to_nfrs[team].append(n)

    # Deduplicate while preserving order
    for team, items in team_to_nfrs.items():
        seen: set[tuple[str, str]] = set()
        unique: List[Nfr] = []
        for n in items:
            key = (n.domain, n.code)
            if key in seen:
                continue
            seen.add(key)
            unique.append(n)
        team_to_nfrs[team] = unique

    # Write index
    lines: List[str] = []
    lines.append("# FtRS NFR – By Team")
    lines.append("")
    lines.append("This page is auto-generated; do not hand-edit.")
    lines.append("")
    lines.append("An NFR appears for a team if the team is listed in `teams` or in any release `team_status`.")
    lines.append("")
    lines.append("## Team Index")
    lines.append("")
    lines.append("| Team | NFR Count | Page |")
    lines.append("|------|-----------|------|")

    for team in sorted(team_to_nfrs.keys()):
        count = len(team_to_nfrs[team])
        page = f"nfr-by-team/{team}/index.md"
        lines.append(f"| {team} | {count} | [{team}]({page}) |")

    TEAM_INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Write per-team pages
    for team, items in team_to_nfrs.items():
        tdir = TEAM_DIR / team
        tdir.mkdir(parents=True, exist_ok=True)
        path = tdir / "index.md"
        lines = []
        lines.append(f"# FtRS NFR – Team {team}")
        lines.append("")
        lines.append("This page is auto-generated; do not hand-edit.")
        lines.append("")
        lines.append("## NFRs")
        lines.append("")
        lines.append("| Domain | NFR | Requirement | Releases | Services |")
        lines.append("|--------|-----|-------------|----------|----------|")

        for n in sorted(items, key=lambda x: (x.domain, x.code)):
            release_ids: List[str] = []
            for r in n.releases:
                # Team participates directly in this release
                if team in r.team_status:
                    release_ids.append(r.id)
            release_str = ", ".join(sorted(set(release_ids))) if release_ids else "-"
            svc_str = ", ".join(n.services) if n.services else "-"
            lines.append(
                f"| {n.domain} | {n.code} | {n.requirement} | {release_str} | {svc_str} |"
            )

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_release_views(nfrs: List[Nfr]) -> None:
    release_to_rows: Dict[str, List[tuple[Nfr, ReleaseInfo]]] = defaultdict(list)

    for n in nfrs:
        for r in n.releases:
            release_to_rows[r.id].append((n, r))

    # Write index
    lines: List[str] = []
    lines.append("# FtRS NFR – By Release")
    lines.append("")
    lines.append("This page is auto-generated; do not hand-edit.")
    lines.append("")
    lines.append("## Release Index")
    lines.append("")
    lines.append("| Release | NFR Count | Page |")
    lines.append("|---------|-----------|------|")

    for rel_id in sorted(release_to_rows.keys()):
        count = len({(n.domain, n.code) for (n, _r) in release_to_rows[rel_id]})
        page = f"nfr-by-release/{rel_id}/index.md"
        lines.append(f"| {rel_id} | {count} | [{rel_id}]({page}) |")

    RELEASE_INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Write per-release pages
    for rel_id, tuples in release_to_rows.items():
        rdir = RELEASE_DIR / rel_id
        rdir.mkdir(parents=True, exist_ok=True)
        path = rdir / "index.md"
        lines = []
        lines.append(f"# FtRS NFR – Release {rel_id}")
        lines.append("")
        lines.append("This page is auto-generated; do not hand-edit.")
        lines.append("")
        lines.append("## NFRs")
        lines.append("")
        lines.append("| Domain | NFR | Teams | Scope (operations) | Status | Team Status |")
        lines.append("|--------|-----|-------|--------------------|--------|-------------|")

        seen: set[tuple[str, str, str]] = set()
        for n, r in sorted(
            tuples, key=lambda t: (t[0].domain, t[0].code)
        ):
            key = (n.domain, n.code, r.id)
            if key in seen:
                continue
            seen.add(key)
            teams = sorted(set(n.teams) | set(r.team_status.keys()))
            teams_str = ", ".join(teams) if teams else "-"
            if r.operations:
                scope = ", ".join(r.operations)
            else:
                scope = "All in-scope operations"
            status = r.overall_status or "-"
            team_status_str = "; ".join(
                f"{t}: {s}" for t, s in sorted(r.team_status.items())
            ) or "-"
            lines.append(
                f"| {n.domain} | {n.code} | {teams_str} | {scope} | {status} | {team_status_str} |"
            )

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_operation_views(nfrs: List[Nfr]) -> None:
    # Index NFRs by operation id
    op_to_nfrs: Dict[str, List[Nfr]] = defaultdict(list)

    for n in nfrs:
        # From explicit operations on the NFR
        for op_id in n.operations:
            op_to_nfrs[op_id].append(n)
        # From release-scoped operations
        for r in n.releases:
            for op_id in r.operations:
                op_to_nfrs[op_id].append(n)

    # Deduplicate
    for op_id, items in op_to_nfrs.items():
        seen: set[tuple[str, str]] = set()
        unique: List[Nfr] = []
        for n in items:
            key = (n.domain, n.code)
            if key in seen:
                continue
            seen.add(key)
            unique.append(n)
        op_to_nfrs[op_id] = unique

    # Write index
    lines: List[str] = []
    lines.append("# FtRS NFR – By Operation")
    lines.append("")
    lines.append("This page is auto-generated; do not hand-edit.")
    lines.append("")
    lines.append("## Operation Index")
    lines.append("")
    lines.append("| Operation ID | NFR Count | Page |")
    lines.append("|--------------|-----------|------|")

    for op_id in sorted(op_to_nfrs.keys()):
        count = len(op_to_nfrs[op_id])
        page = f"nfr-by-operation/{op_id}/index.md"
        lines.append(f"| {op_id} | {count} | [{op_id}]({page}) |")

    OP_INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Write per-operation pages
    for op_id, items in op_to_nfrs.items():
        odir = OP_DIR / op_id
        odir.mkdir(parents=True, exist_ok=True)
        path = odir / "index.md"
        lines = []
        lines.append(f"# FtRS NFR – Operation {op_id}")
        lines.append("")
        lines.append("This page is auto-generated; do not hand-edit.")
        lines.append("")
        lines.append("## NFRs")
        lines.append("")
        lines.append("| Domain | NFR | Releases | Teams | Services |")
        lines.append("|--------|-----|----------|-------|----------|")

        for n in sorted(items, key=lambda x: (x.domain, x.code)):
            rel_ids: List[str] = []
            for r in n.releases:
                # Include releases where this operation is explicitly listed, or
                # where operations is empty/omitted (meaning cross-cutting)
                if not r.operations or op_id in r.operations:
                    rel_ids.append(r.id)
            releases_str = ", ".join(sorted(set(rel_ids))) if rel_ids else "-"
            teams = sorted(set(n.teams))
            teams_str = ", ".join(teams) if teams else "-"
            svc_str = ", ".join(n.services) if n.services else "-"
            lines.append(
                f"| {n.domain} | {n.code} | {releases_str} | {teams_str} | {svc_str} |"
            )

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not YAML_AVAILABLE:
        raise SystemExit("PyYAML is required to run this script")

    ensure_dirs()
    nfrs = load_all_nfrs()

    build_team_views(nfrs)
    build_release_views(nfrs)
    build_operation_views(nfrs)


if __name__ == "__main__":
    main()
