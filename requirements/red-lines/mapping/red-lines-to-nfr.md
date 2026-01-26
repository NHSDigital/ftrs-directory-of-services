# Red Lines → NFR / Control Mapping

source: requirements/red-lines/overview.md
created_at: 2025-11-27
purpose: Map Red Lines to internal NFRs/controls (regenerated from updated overview)
status: draft

This scaffold links each Red Line reference to internal non-functional requirements (NFRs) or governance controls. Use it to track coverage and ownership.

## Mapping Table (regenerated)

| Ref     | Category | Summary                                                                                                      | Proposed NFR/Control             | Status   | Owner | Evidence | ReviewDate | Notes                                              |
| ------- | -------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------- | -------- | ----- | -------- | ---------- | -------------------------------------------------- |
| Cloud-1 | Cloud    | Public cloud; product-owned accounts; AWS Landing Zone; Azure NHSE-LZ-Root; internet-first; governance items | NFR-CLOUD-GOV-01                 | proposed | TBD   | TBD      | TBD        | Includes account separation; internet-first policy |
| Cloud-2 | Cloud    | Internet-first; HSCN only for legacy connections                                                             | CTRL-NET-INTERNET-FIRST-01       | proposed | TBD   | TBD      | TBD        | Confirm legacy exception handling                  |
| Cloud-3 | Cloud    | Autoscale down ≥40% from peak to off-peak; infra fully utilised                                              | NFR-CAPACITY-UTIL-01             | proposed | TBD   | TBD      | TBD        | Inventory/unnecessary resources principle          |
| Cloud-4 | Cloud    | Zero-downtime blue/green deployments for gold/platinum                                                       | CTRL-DEPLOY-BLUEGREEN-01         | proposed | TBD   | TBD      | TBD        | Applies to gold/platinum tiers                     |
| Cloud-5 | Cloud    | DR: full restore test from production backups ≥24 months; rebuild on new account                             | NFR-DR-RESTORE-TEST-01           | proposed | TBD   | TBD      | TBD        | Align with backup scenario guidance                |
| Cloud-6 | Cloud    | Immutable backups; annual restore validation; additional measures if RPO=0; use cloud blueprints             | NFR-BACKUP-IMMUTABLE-01          | proposed | TBD   | TBD      | TBD        | Blueprint compliance required                      |
| Cloud-7 | Cloud    | Active-passive: swap sites at least every 12 months                                                          | NFR-OPERATIONS-ACTIVE-PASSIVE-01 | proposed | TBD   | TBD      | TBD        | Operational calendar action                        |
| Cloud-8 | Cloud    | No standing prod write; time-bound elevation ≤24h with approval; AWS CCOE / Azure PIM                        | CTRL-ACCESS-PROD-ELEVATION-01    | proposed | TBD   | TBD      | TBD        | Privileged access mgmt patterns                    |
| Reuse-1 | Shared   | Use NHS Notify for citizen communications                                                                    | CTRL-COMMS-NOTIFY-01             | proposed | TBD   | TBD      | TBD        | Staff equivalent TBD                               |
| Reuse-2 | Shared   | PDS as single source of truth for demographics; no overrides                                                 | CTRL-DATA-SOT-PDS-01             | proposed | TBD   | TBD      | TBD        | Data governance alignment                          |
| Reuse-3 | Shared   | Citizen auth via NHS login; proxy access currently unsupported                                               | CTRL-AUTH-NHSLOGIN-01            | proposed | TBD   | TBD      | TBD        | Document proxy exception                           |
| Reuse-4 | Shared   | IAL3→CIS2; else CIS2/NHS.net per NIST IAL levels                                                             | CTRL-IDENTITY-ASSURANCE-01       | proposed | TBD   | TBD      | TBD        | Include NIST IAL references                        |
| Reuse-5 | Shared   | Consult FDP/CDP; avoid building analytics platforms; use cloud-native for simple analysis                    | CTRL-ANALYTICS-GOV-01            | proposed | TBD   | TBD      | TBD        | Reuse-first principle                              |
| Reuse-6 | Shared   | National cohorting via Cohorting As A Service                                                                | CTRL-COHORTING-CAAS-01           | proposed | TBD   | TBD      | TBD        | National scope                                     |
| Reuse-7 | Shared   | Align with `nhsuk-frontend` and NHS Design System; contribute components; use `nhsuk-react-components`       | CTRL-UX-DESIGN-SYSTEM-01         | proposed | TBD   | TBD      | TBD        | UI WG alignment                                    |
| SDLC-1  | SDLC     | Use NHS GitHub Enterprise; secure repos; engineering dashboards auto-collect                                 | CTRL-REPOS-SEC-ENG-01            | proposed | TBD   | TBD      | TBD        | Enterprise governance                              |
| SDLC-2  | SDLC     | SonarCloud quality gates; total unit test coverage > 50%                                                     | NFR-QUALITY-SONAR-01             | proposed | TBD   | TBD      | TBD        | CI metrics linkage                                 |
| SDLC-3  | SDLC     | Build and deploy to production at least quarterly                                                            | NFR-DELIVERY-CADENCE-QTR-01      | proposed | TBD   | TBD      | TBD        | Even without code changes                          |
| SDLC-4  | SDLC     | Automate all planned production deployments                                                                  | CTRL-CI-CD-AUTO-01               | proposed | TBD   | TBD      | TBD        | Change windows respected                           |
| SDLC-5  | SDLC     | Build daily; deploy at least every two weeks (outside freeze)                                                | NFR-DELIVERY-CADENCE-BIWK-01     | proposed | TBD   | TBD      | TBD        | Active development                                 |
| SDLC-6  | SDLC     | Architect-for-flow; bounded contexts; independent deployability                                              | NFR-ARCH-BOUNDED-CONTEXT-01      | proposed | TBD   | TBD      | TBD        | Pattern adherence                                  |
| Soft-1  | Mgmt     | APIs must follow published guidance                                                                          | CTRL-API-GOV-01                  | proposed | TBD   | TBD      | TBD        | Policies + WGL                                     |
| Soft-2  | Mgmt     | Use DOS for externally-facing APIs; no SCALs                                                                 | CTRL-API-ONBOARD-DOS-01          | proposed | TBD   | TBD      | TBD        | Onboarding control                                 |
| Soft-3  | Mgmt     | SBOM required; no EOL; version policies; update ≤6 months; CVM patches                                       | CTRL-SBOM-VERSION-CVM-01         | proposed | TBD   | TBD      | TBD        | Prefer latest stable                               |
| Soft-4  | Mgmt     | Quarterly maturity review using Software Quality Framework                                                   | CTRL-MATURITY-REVIEW-01          | proposed | TBD   | TBD      | TBD        | Cadence 90 days                                    |
| Soft-5  | Mgmt     | Tech Radar alignment; approvals/migrations for CONTAIN/PROPOSED/AVOID                                        | CTRL-TECH-RADAR-ALIGN-01         | proposed | TBD   | TBD      | TBD        | Migration plans for AVOID                          |
| Soft-6  | Mgmt     | Comply with mandatory blueprints ≤6 months                                                                   | CTRL-BLUEPRINTS-COMPLIANCE-01    | proposed | TBD   | TBD      | TBD        | Mandate-driven                                     |
| Soft-7  | Mgmt     | Avoid dependencies near retirement (≤6 months) unless retiring first                                         | CTRL-DEPENDENCY-LIFECYCLE-01     | proposed | TBD   | TBD      | TBD        | Retirement window                                  |
| Soft-8  | Mgmt     | Avoid network dependencies with retiring protocols (≤6 months) unless retiring first                         | CTRL-PROTOCOL-LIFECYCLE-01       | proposed | TBD   | TBD      | TBD        | TLS/support changes                                |
| Spine-1 | Spine    | Retire Riak by end of 2027                                                                                   | CTRL-DB-RIAK-RETIRE-01           | proposed | TBD   | TBD      | TBD        | Spine-only red line                                |

### Ownership & Verification

- Owner: Add team/role responsible per row
- Evidence: Link to dashboards, CI reports, change records, ADRs
- Review cadence: Quarterly (align with maturity reviews)
