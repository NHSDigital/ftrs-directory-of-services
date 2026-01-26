# Reliability & Resilience NFRs

Background:
Reliability is the outcome (consistent acceptable service), resilience is how we achieve it (withstanding faults, attacks, dependencies failures, and operational events). Production FtRS must eliminate single points of failure, degrade gracefully, and recover within defined RTO/RPO targets alongside security attack resistance and robust backup strategies.

Scope:

- Production environment only.
- Includes application tiers, data, networking, external integrations, batch processes, and operational tooling.

Legend: Code | Requirement | Rationale | Verification | Tags

## NFR Table

| Code    | Requirement                                                                                                | Rationale                                 | Verification                                     | Tags                             |
| ------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------ | -------------------------------- |
| REL-001 | Critical APIs achieve ≥99.9% monthly availability                                                          | Minimise downtime impact                  | Availability report & synthetic checks           | reliability, availability        |
| REL-002 | Multi-AZ deployment with no single points of failure (SPOF)                                                | Sustain service during AZ or node loss    | Architecture review & AZ failure simulation      | reliability, multi-az, spof      |
| REL-003 | Adopt cloud Well-Architected reliability pillar practices across lifecycle                                 | Embed best practices early                | Checklist reviews at design/delivery/maintenance | reliability, governance          |
| REL-004 | Resilience to volumetric Denial of Service attacks                                                         | Maintain service under traffic floods     | WAF/DDoS shield test & rate limiting metrics     | reliability, security, dos       |
| REL-005 | Resilience against code injection (input validation & sandboxing)                                          | Prevent malicious code execution          | Static analysis + injection simulation tests     | reliability, security, injection |
| REL-006 | Side-channel isolation (no tenant co-location for sensitive workloads)                                     | Prevent leakage via co-residency          | Infrastructure placement policy & scan           | reliability, security, isolation |
| REL-007 | Resilience to authentication attacks (brute force, replay, phishing)                                       | Protect credential integrity              | Auth rate limiting + MFA + anomaly alerts        | reliability, security, auth      |
| REL-008 | Man-in-the-Middle prevention (strict TLS + cert pinning where applicable)                                  | Ensure channel integrity                  | TLS scan + pinning verification tests            | reliability, security, mitm      |
| REL-009 | Clickjacking prevention (X-Frame-Options / CSP frame-ancestors)                                            | Protect user interactions                 | Header inspection & iframe attempt test          | reliability, security, ux        |
| REL-010 | Support suspension & resumption of batch processes without data corruption                                 | Safe housekeeping operations              | Batch run interruption test & checksum compare   | reliability, process, batch      |
| REL-011 | Continuous compute health checks & automatic unhealthy node replacement                                    | Avoid degraded performance from bad nodes | Health probe logs & auto-replacement events      | reliability, compute, healing    |
| REL-012 | Single node loss tolerance in any functional group without performance/data degradation until replacement         | Maintain SLA under partial failure        | Chaos test removing node; metrics stable         | reliability, fault-tolerance     |
| REL-013 | Tier resilience (presentation/service/data) with graceful degradation & recovery                           | Preserve core functionality               | Simulated tier failures & user experience tests  | reliability, tier, graceful      |
| REL-014 | External system failure resilience (SSB/CIS2, SDS, ODS, NHS.UK, PDS, SIEM) with fallback or graceful error | Minimise dependency impact                | Stub outage simulations; fallback paths verified | reliability, dependency          |
| REL-015 | Load balancer resilience (presentation/app tier) – fail-over without session loss                           | Maintain session continuity               | LB failure simulation; sticky session validation | reliability, networking          |
| REL-016 | Graceful server-side error handling (logout or user message)                                               | Improve UX & security posture             | Error injection tests display appropriate action | reliability, ux, error           |
| REL-017 | Comprehensive backup & recovery strategy meeting NHS policy & ransomware defenses (RPO/RTO alignment)      | Recover from catastrophic events quickly  | Backup schedule audit; restore drill success     | reliability, backup, ransomware  |

## Verification Strategy

- Chaos engineering for node/tier/LB failures.
- Security attack simulations (DoS, injection, auth brute force, MITM attempts).
- Automated header & configuration inspections (CSP, X-Frame-Options, TLS).
- Batch job suspend/resume integrity tests (pre/post checksums).
- Health check and auto-replacement event log correlation.
- External dependency outage staging via mocks/stubs.
- Backup restore drills & ransomware scenario test (isolation + immutable copy).

## Follow-Up Items

- Define quantitative thresholds for DoS resilience (max sustainable RPS before mitigation) for REL-004.
- Specify node health probe intervals & replacement SLO for REL-011.
- Document fallback strategies per external system for REL-014.
- Add immutable storage verification & air-gap backup test for REL-017.
