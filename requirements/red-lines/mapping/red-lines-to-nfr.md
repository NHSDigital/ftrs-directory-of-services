source: requirements/red-lines/overview.md
created_at: 2025-11-27
purpose: Map Red Lines to internal NFRs/controls (regenerated from updated overview)
status: draft
---

# Red Lines → NFR / Control Mapping

This scaffold links each Red Line reference to internal non-functional requirements (NFRs) or governance controls. Use it to track coverage and ownership.

### Mapping Table (regenerated)

| Ref | Category | Summary | Proposed NFR/Control | Status | Owner | Evidence | ReviewDate | Notes |
|-----|----------|---------|-----------------------|--------|-------|----------|-----------|-------|
| Cloud-1 | Cloud | Public cloud; product-owned accounts; AWS Landing Zone; Azure NHSE-LZ-Root; internet-first; governance items | NFR-CLOUD-GOV-01 | proposed |  |  |  | Includes account separation; internet-first policy |
| Cloud-2 | Cloud | Internet-first; HSCN only for legacy connections | CTRL-NET-INTERNET-FIRST-01 | proposed |  |  |  | Confirm legacy exception handling |
| Cloud-3 | Cloud | Autoscale down ≥40% from peak to off-peak; infra fully utilised | NFR-CAPACITY-UTIL-01 | proposed |  |  |  | Inventory/unnecessary resources principle |
| Cloud-4 | Cloud | Zero-downtime blue/green deployments for gold/platinum | CTRL-DEPLOY-BLUEGREEN-01 | proposed |  |  |  | Applies to gold/platinum tiers |
| Cloud-5 | Cloud | DR: full restore test from production backups ≥24 months; rebuild on new account | NFR-DR-RESTORE-TEST-01 | proposed |  |  |  | Align with backup scenario guidance |
| Cloud-6 | Cloud | Immutable backups; annual restore validation; additional measures if RPO=0; use cloud blueprints | NFR-DR-IMMUTABLE-01 | proposed |  |  |  | Blueprint compliance required |
| Cloud-7 | Cloud | Active-passive: swap sites at least every 12 months | NFR-OPERATIONS-ACTIVE-PASSIVE-01 | proposed |  |  |  | Operational calendar action |
| Cloud-8 | Cloud | No standing prod write; time-bound elevation ≤24h with approval; AWS CCOE / Azure PIM | CTRL-ACCESS-PROD-ELEVATION-01 | proposed |  |  |  | Privileged access mgmt patterns |
| Reuse-1 | Shared | Use NHS Notify for citizen communications | CTRL-COMMS-NOTIFY-01 | proposed |  |  |  | Staff equivalent TBD |
| Reuse-2 | Shared | PDS as single source of truth for demographics; no overrides | CTRL-DATA-SOT-PDS-01 | proposed |  |  |  | Data governance alignment |
| Reuse-3 | Shared | Citizen auth via NHS login; proxy access currently unsupported | CTRL-AUTH-NHSLOGIN-01 | proposed |  |  |  | Document proxy exception |
| Reuse-4 | Shared | IAL3→CIS2; else CIS2/NHS.net per NIST IAL levels | CTRL-IDENTITY-ASSURANCE-01 | proposed |  |  |  | Include NIST IAL references |
| Reuse-5 | Shared | Consult FDP/CDP; avoid building analytics platforms; use cloud-native for simple analysis | CTRL-ANALYTICS-GOV-01 | proposed |  |  |  | Reuse-first principle |
| Reuse-6 | Shared | National cohorting via Cohorting As A Service | CTRL-COHORTING-CAAS-01 | proposed |  |  |  | National scope |
| Reuse-7 | Shared | Align with `nhsuk-frontend` and NHS Design System; contribute components; use `nhsuk-react-components` | CTRL-UX-DESIGN-SYSTEM-01 | proposed |  |  |  | UI WG alignment |
| SDLC-1 | SDLC | Use NHS GitHub Enterprise; secure repos; engineering dashboards auto-collect | CTRL-REPOS-SEC-ENG-01 | proposed |  |  |  | Enterprise governance |
| SDLC-2 | SDLC | SonarCloud quality gates; total unit test coverage > 50% | NFR-QUALITY-SONAR-01 | proposed |  |  |  | CI metrics linkage |
| SDLC-3 | SDLC | Build and deploy to production at least quarterly | NFR-DELIVERY-CADENCE-QTR-01 | proposed |  |  |  | Even without code changes |
| SDLC-4 | SDLC | Automate all planned production deployments | CTRL-CI-CD-AUTO-01 | proposed |  |  |  | Change windows respected |
| SDLC-5 | SDLC | Build daily; deploy at least every two weeks (outside freeze) | NFR-DELIVERY-CADENCE-BIWK-01 | proposed |  |  |  | Active development |
| SDLC-6 | SDLC | Architect-for-flow; bounded contexts; independent deployability | NFR-ARCH-BOUNDED-CONTEXT-01 | proposed |  |  |  | Pattern adherence |
| Soft-1 | Mgmt | APIs must follow published guidance | CTRL-API-GOV-01 | proposed |  |  |  | Policies + WGL |
| Soft-2 | Mgmt | Use DOS for externally-facing APIs; no SCALs | CTRL-API-ONBOARD-DOS-01 | proposed |  |  |  | Onboarding control |
| Soft-3 | Mgmt | SBOM required; no EOL; version policies; update ≤6 months; CVM patches | CTRL-SBOM-VERSION-CVM-01 | proposed |  |  |  | Prefer latest stable |
| Soft-4 | Mgmt | Quarterly maturity review using Software Quality Framework | CTRL-MATURITY-REVIEW-01 | proposed |  |  |  | Cadence 90 days |
| Soft-5 | Mgmt | Tech Radar alignment; approvals/migrations for CONTAIN/PROPOSED/AVOID | CTRL-TECH-RADAR-ALIGN-01 | proposed |  |  |  | Migration plans for AVOID |
| Soft-6 | Mgmt | Comply with mandatory blueprints ≤6 months | CTRL-BLUEPRINTS-COMPLIANCE-01 | proposed |  |  |  | Mandate-driven |
| Soft-7 | Mgmt | Avoid dependencies near retirement (≤6 months) unless retiring first | CTRL-DEPENDENCY-LIFECYCLE-01 | proposed |  |  |  | Retirement window |
| Soft-8 | Mgmt | Avoid network dependencies with retiring protocols (≤6 months) unless retiring first | CTRL-PROTOCOL-LIFECYCLE-01 | proposed |  |  |  | TLS/support changes |
| SDLC-4 | SDLC | Automate planned prod deployments | CTRL-CI-CD-01 | proposed | Manual change windows excluded |
| SDLC-5 | SDLC | Daily builds; deploy every two weeks | NFR-DELIVERY-CADENCE-02 | proposed | Outside freeze windows |
| SDLC-6 | SDLC | Architect-for-flow; bounded contexts | NFR-ARCH-BOUNDED-01 | proposed | Independent deployability |
| Soft-1 | Mgmt | API guidance; DOS onboarding | CTRL-API-GOV-01 | proposed | No SCALs |
| Soft-2 | Mgmt | Maintain SBOM centrally | CTRL-SBOM-01 | proposed | Contribute to central approach |
| Soft-3 | Mgmt | No EOL software; patch CVM; update ≤6 months | CTRL-VULN-MGMT-01 | proposed | Prefer latest stable |
| Soft-4 | Mgmt | Quarterly maturity review | CTRL-MATURITY-01 | proposed | Software Quality Framework |
| Soft-5 | Mgmt | Tech Radar alignment; approvals/migrations | CTRL-TECH-RADAR-01 | proposed | AVOID → migration plan |
| Soft-6 | Mgmt | Comply with mandated blueprints ≤6 months | CTRL-BLUEPRINTS-02 | proposed | Triggered by mandate |
| Soft-7 | Mgmt | Avoid dependencies near retirement | CTRL-DEPENDENCY-LIFECYCLE-01 | proposed | 6-month retirement window |
| Soft-8 | Mgmt | Avoid retiring security protocols | CTRL-PROTOCOL-LIFECYCLE-01 | proposed | 6-month retirement window |
| Spine-1 | Spine | Retire Riak by end of 2027 | CTRL-DB-RIAK-RETIRE-01 | proposed | Spine-only red line |

### Ownership & Verification
- Owner: Add team/role responsible per row
- Evidence: Link to dashboards, CI reports, change records, ADRs
- Review cadence: Quarterly (align with maturity reviews)
