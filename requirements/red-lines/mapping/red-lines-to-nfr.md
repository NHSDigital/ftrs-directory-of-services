---
source: requirements/red-lines/overview.md
created_at: 2025-11-26
purpose: Map Red Lines to internal NFRs/controls
status: draft
---

# Red Lines → NFR / Control Mapping

This scaffold links each Red Line reference to internal non-functional requirements (NFRs) or governance controls. Use it to track coverage and ownership.

### How to use
- Update `Proposed NFR/Control` with the canonical ID(s) from your NFR catalogue.
- Set `Status` to `proposed`, `agreed`, or `verified`.
- Add concise `Notes` (e.g., exceptions, scope, or owning team).

### Verification Checklist (maintained here as single source)
- [ ] Each Ref has ≥1 Proposed NFR/Control ID
- [ ] Status advanced from `proposed` to `agreed`/`verified` after review
- [ ] Owner filled (team or role) per Ref
- [ ] Evidence links (dashboard / ADR / CI) present
- [ ] ReviewDate within last 90 days
- [ ] Exceptions documented where partial applicability
- [ ] No deprecated control IDs

### Index
- Cloud / Infrastructure: Cloud-1 … Cloud-8
- Using Shared Services: Reuse-1 … Reuse-7
- Software Development Lifecycle: SDLC-1 … SDLC-6
- Software Management: Soft-1 … Soft-8
- Team-Specific (Spine): Spine-1

### Mapping Table

| Ref | Category | Summary | Proposed NFR/Control | Status | Owner | Evidence | ReviewDate | Notes |
|-----|----------|---------|-----------------------|--------|-------|----------|-----------|-------|
| Cloud-1 | Cloud | Public cloud; account governance; internet-first; autoscale; blue/green; DR test | NFR-CLOUD-GOV-01, NFR-DR-01 | proposed |  |  |  | Confirm autoscale threshold applicability per product |
| Cloud-2 | Cloud | Immutable backups; annual restore validation; RPO considerations | NFR-DR-IMMUTABLE-01 | proposed |  |  |  | Align with backup blueprint |
| Cloud-3 | Cloud | Active/passive swap annually | NFR-DR-OPERATIONS-02 | proposed |  |  |  | Schedule in ops calendar |
| Cloud-4 | Cloud | Use mandatory cloud blueprints | CTRL-BLUEPRINTS-01 | proposed |  |  |  | Compliance window 6 months |
| Cloud-5 | Cloud | Infra utilization + auto-scaling | NFR-CAPACITY-01 | proposed |  |  |  | Monitor via cost/util dashboards |
| Cloud-6 | Cloud | Resilience test scenarios | NFR-RESILIENCE-TESTS-01 | proposed |  |  |  | Tie to change calendar |
| Cloud-7 | Cloud | Define/test cloud backups | NFR-BACKUP-01 | proposed |  |  |  | Immutable target required |
| Cloud-8 | Cloud | No standing prod write; time-bound elevation | CTRL-ACCESS-PROD-01 | proposed |  |  |  | AWS CCOE / Azure PIM patterns |
| Reuse-1 | Shared | Use NHS Notify for citizen comms | CTRL-COMMS-NOTIFY-01 | proposed |  |  |  | Staff comms exception noted |
| Reuse-2 | Shared | PDS is source of truth for demographics | CTRL-DATA-SOT-01 | proposed |  |  |  | No overrides outside PDS |
| Reuse-3 | Shared | Citizen auth via NHS login | CTRL-AUTH-NHSLOGIN-01 | proposed |  |  |  | Proxy access exception |
| Reuse-4 | Shared | IAL3 → CIS2; else CIS2 or NHS.net | CTRL-IDENTITY-IAL-01 | proposed |  |  |  | Reference NIST IAL |
| Reuse-5 | Shared | Consult FDP/CDP; don’t build platforms | CTRL-ANALYTICS-GOV-01 | proposed |  |  |  | Use cloud-native for simple cases |
| Reuse-6 | Shared | Cohorting via CAAS | CTRL-COHORTING-01 | proposed |  |  |  | National cohorting only |
| Reuse-7 | Shared | Align with NHS Design System | CTRL-UX-DESIGN-01 | proposed |  |  |  | Contribute components back |
| SDLC-1 | SDLC | Use NHS GitHub; securing-repos; dashboards | CTRL-SC-REPOS-01 | proposed |  |  |  | Enterprise org coverage |
| SDLC-2 | SDLC | SonarCloud quality gates; >50% coverage | NFR-QUALITY-TESTS-01 | proposed |  |  |  | Track in CI metrics |
| SDLC-3 | SDLC | Quarterly prod build/deploy | NFR-DELIVERY-CADENCE-01 | proposed |  |  |  | Even with no code changes |
| SDLC-4 | SDLC | Automate planned prod deployments | CTRL-CI-CD-01 | proposed |  |  |  | Manual change windows excluded |
| SDLC-5 | SDLC | Daily builds; deploy every two weeks | NFR-DELIVERY-CADENCE-02 | proposed |  |  |  | Outside freeze windows |
| SDLC-6 | SDLC | Architect-for-flow; bounded contexts | NFR-ARCH-BOUNDED-01 | proposed |  |  |  | Independent deployability |
| Soft-1 | Mgmt | API guidance; DOS onboarding | CTRL-API-GOV-01 | proposed |  |  |  | No SCALs |
| Soft-2 | Mgmt | Maintain SBOM centrally | CTRL-SBOM-01 | proposed |  |  |  | Contribute to central approach |
| Soft-3 | Mgmt | No EOL software; patch CVM; update ≤6 months | CTRL-VULN-MGMT-01 | proposed |  |  |  | Prefer latest stable |
| Soft-4 | Mgmt | Quarterly maturity review | CTRL-MATURITY-01 | proposed |  |  |  | Software Quality Framework |
| Soft-5 | Mgmt | Tech Radar alignment; approvals/migrations | CTRL-TECH-RADAR-01 | proposed |  |  |  | AVOID → migration plan |
| Soft-6 | Mgmt | Comply with mandated blueprints ≤6 months | CTRL-BLUEPRINTS-02 | proposed |  |  |  | Triggered by mandate |
| Soft-7 | Mgmt | Avoid dependencies near retirement | CTRL-DEPENDENCY-LIFECYCLE-01 | proposed |  |  |  | 6-month retirement window |
| Soft-8 | Mgmt | Avoid retiring security protocols | CTRL-PROTOCOL-LIFECYCLE-01 | proposed |  |  |  | 6-month retirement window |
| Spine-1 | Spine | Retire Riak by end of 2027 | CTRL-DB-RIAK-RETIRE-01 | proposed |  |  |  | Spine-only red line |

### Ownership & Verification
- Owner: Add team/role responsible per row
- Evidence: Link to dashboards, CI reports, change records, ADRs
- Review cadence: Quarterly (align with maturity reviews)
