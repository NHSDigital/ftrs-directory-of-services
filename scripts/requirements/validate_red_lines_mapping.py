#!/usr/bin/env python3
"""Validate red lines to NFR/control mapping.

Checks:
- Proposed NFR/Control present
- Status not empty (and one of allowed values)
- Owner present
- Evidence present
- ReviewDate present and within last 90 days
- Notes present (optional but flagged if empty)
Outputs JSON summary plus a human-readable table of issues.
"""
from __future__ import annotations
import re, sys, json, datetime, pathlib
ALLOWED_STATUS = {"proposed", "agreed", "verified"}
AGE_LIMIT_DAYS = 90

def parse_table(md: str):
    lines = md.splitlines()
    in_table = False
    header = []
    rows = []
    for line in lines:
        if line.startswith('| Ref '):
            in_table = True
            header = [h.strip() for h in line.strip().split('|')[1:-1]]
            continue
        if in_table:
            if not line.startswith('|'):
                break
            if re.match(r'^\|[- ]+\|', line):
                # separator row
                continue
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) != len(header):
                continue
            rows.append(dict(zip(header, parts)))
    return header, rows

def validate(rows):
    today = datetime.date.today()
    issues = []
    for r in rows:
        ref = r.get('Ref')
        # Proposed NFR/Control
        if not r.get('Proposed NFR/Control'):
            issues.append((ref, 'missing_nfr_control'))
        # Status
        status = r.get('Status','').lower()
        if not status:
            issues.append((ref, 'missing_status'))
        elif status not in ALLOWED_STATUS:
            issues.append((ref, f'invalid_status:{status}'))
        # Owner
        if not r.get('Owner'):
            issues.append((ref, 'missing_owner'))
        # Evidence
        if not r.get('Evidence'):
            issues.append((ref, 'missing_evidence'))
        # ReviewDate
        rd = r.get('ReviewDate')
        if not rd:
            issues.append((ref, 'missing_review_date'))
        else:
            try:
                dt = datetime.date.fromisoformat(rd)
                age = (today - dt).days
                if age > AGE_LIMIT_DAYS:
                    issues.append((ref, f'review_date_stale:{age}d'))
            except ValueError:
                issues.append((ref, 'invalid_review_date_format'))
        # Notes optional but flag if empty to encourage context
        if not r.get('Notes'):
            issues.append((ref, 'missing_notes'))
    return issues

def main():
    mapping_path = pathlib.Path('requirements/red-lines/mapping/red-lines-to-nfr.md')
    if not mapping_path.exists():
        print(json.dumps({'error':'mapping file not found','path':str(mapping_path)}))
        return
    md = mapping_path.read_text(encoding='utf-8')
    header, rows = parse_table(md)
    issues = validate(rows)
    summary = {
        'total_records': len(rows),
        'records_missing_owner': len([i for i in issues if i[1]=='missing_owner']),
        'records_missing_evidence': len([i for i in issues if i[1]=='missing_evidence']),
        'records_missing_review_date': len([i for i in issues if i[1]=='missing_review_date']),
        'stale_or_invalid_review_dates': len([i for i in issues if i[1].startswith('review_date_stale') or i[1]=='invalid_review_date_format']),
        'missing_notes': len([i for i in issues if i[1]=='missing_notes']),
        'invalid_status': len([i for i in issues if i[1].startswith('invalid_status')]),
    }
    output = {
        'header': header,
        'summary': summary,
        'issues': issues,
    }
    print(json.dumps(output, indent=2))
    # Human-readable
    if issues:
        print('\nIssues:')
        for ref, code in issues:
            print(f'- {ref}: {code}')
    else:
        print('\nNo issues found.')

if __name__ == '__main__':
    main()
