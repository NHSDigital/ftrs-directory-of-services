# NFR Cross Reference Matrix

| NFR Code | Domain | Related User Stories | Acceptance Criteria Anchor |
|----------|--------|----------------------|----------------------------|
| SEC-001  | Security | STORY-001, STORY-010 | Crypto algorithms conform; weak ciphers rejected |
| SEC-003  | Security | STORY-011, STORY-176, STORY-182 | All endpoints TLS only; storage encryption enabled |
| SEC-007  | Security | STORY-012 | SG rules audited; attempt broad ingress denied |
| SEC-025  | Security | STORY-013 | PID requests enforce mTLS; plaintext blocked |
| SEC-027  | Security | STORY-014, STORY-182 | Build fails on high CVE; report archived |
| PERF-001 | Performance | STORY-005, STORY-021, STORY-176, STORY-180 | Latency thresholds p50/p95 logged & asserted |
| REL-001  | Reliability | STORY-002, STORY-018 | Health checks, multi-AZ deployment documented |
| OBS-001  | Observability | STORY-030 | App & infra health panels show green |
| OBS-005  | Observability | STORY-031 | Performance metrics per layer present |
| OBS-008  | Observability | STORY-032 | TPS per endpoint displayed & threshold alert configured |
| OBS-011  | Observability | STORY-033 | Failure types logged & classified in dashboard |
| OBS-013  | Observability | STORY-034 | Infra log query returns expected fields |
| OBS-019  | Observability | STORY-035, STORY-176 | Operational log shows full transaction chain |
| OBS-022  | Observability | STORY-036 | Audit trail reconstructs user action |
| OBS-024  | Observability | STORY-037 | Alert rule triggers multi-channel notification |
| OBS-026  | Observability | STORY-038 | Analytics query identifies usage pattern |
| OBS-028  | Observability | STORY-039 | RBAC restricts dashboard sections |
| OBS-030  | Observability | STORY-040, STORY-176 | Distributed trace spans cover end-to-end request |
| SEC-002  | Security | STORY-041 | WAF security pillar checklist completed & gaps tracked |
| SEC-004  | Security | STORY-042 | Storage services show encryption enabled |
| SEC-005  | Security | STORY-043 | Cross-env data access attempts denied |
| SEC-006  | Security | STORY-044 | No direct prod console queries detected in audit period |
| SEC-008  | Security | STORY-045 | Perimeter scan shows no broad whitelist & secure channels |
| SEC-009  | Security | STORY-046, STORY-177, STORY-182 | ASVS & CIS benchmark automation reports pass thresholds |
| SEC-010  | Security | STORY-047 | Annual pen test executed; remediation tickets raised & closed |
| SEC-011  | Security | STORY-048 | Security features enabled latency within SLA |
| SEC-012  | Security | STORY-049 | IAM policy review confirms least privilege for system roles |
| SEC-013  | Security | STORY-050 | Key rotation events logged; unauthorized access denied |
| SEC-014  | Security | STORY-051 | mTLS handshake succeeds between designated services |
| SEC-015  | Security | STORY-052 | Expiry alert fired in advance; renewal executed seamlessly |
| SEC-016  | Security | STORY-053 | MFA enforced for all privileged infra roles |
| SEC-017  | Security | STORY-054 | Scan reports zero unmanaged long-lived credentials |
| SEC-018  | Security | STORY-055 | Supplier audit attestation stored & verified |
| SEC-019  | Security | STORY-056 | Segmentation test confirms tenant isolation |
| SEC-020  | Security | STORY-057 | Remote connections present valid Authority certs |
| SEC-021  | Security | STORY-058 | Port scan matches approved diagnostic list only |
| SEC-022  | Security | STORY-059 | Utility program access restricted to approved roles |
| SEC-023  | Security | STORY-060 | Deployment provenance shows unique traceable accounts |
| SEC-024  | Security | STORY-061 | Code/data transfer logs show integrity & secure channels |
| SEC-026  | Security | STORY-062 | API responses contain no unencrypted PID fields |
| SEC-028  | Security | STORY-063, STORY-182 | Release pipeline blocks on critical unresolved findings |
| SCAL-001 | Scalability | STORY-070, STORY-181 | Horizontal scale-out increases TPS linearly within tolerance |
| SCAL-002 | Scalability | STORY-071 | Vertical resize retains data & function without downtime |
| SCAL-003 | Scalability | STORY-072 | All layers pass scalability checklist |
| SCAL-004 | Scalability | STORY-073 | Scale-down events occur after sustained low utilisation |
| SCAL-005 | Scalability | STORY-074, STORY-184 | Autoscaling policy simulation triggers controlled scale |
| SCAL-006 | Scalability | STORY-075 | Scale event shows no SLA breach in latency/error |
| SCAL-007 | Scalability | STORY-076 | Capacity report shows ≥30% headroom |
| SCAL-008 | Scalability | STORY-077 | No manual scaling tickets for variance period |
| SCAL-009 | Scalability | STORY-078 | Audit logs capture actor/reason for scaling |
| SCAL-010 | Scalability | STORY-079 | Predictive alert fires at utilisation forecast threshold |
| AVAIL-001 | Availability | STORY-080 | Availability report shows ≥99.90% multi-AZ uptime |
| AVAIL-002 | Availability | STORY-081 | Region DR simulation meets plan objectives |
| AVAIL-003 | Availability | STORY-082 | Uptime monitoring confirms 24x7 coverage |
| AVAIL-004 | Availability | STORY-083 | Monthly maintenance minutes ≤150; single ≤60 |
| AVAIL-005 | Availability | STORY-084 | Tuesday window executed; smoke tests pass |
| AVAIL-006 | Availability | STORY-085 | DR exercise restores service <2h |
| AVAIL-007 | Availability | STORY-086 | Replication lag ≤60s; failover data delta minimal |
| AVAIL-008 | Availability | STORY-087 | API uptime aligns with core service |
| AVAIL-009 | Availability | STORY-088 | Non-UK access attempts blocked & logged |
| AVAIL-010 | Availability | STORY-089, STORY-181 | Blue/green deployment produces 0 failed requests |
| REL-002  | Reliability | STORY-090, STORY-176, STORY-181 | AZ failure simulation maintains service |
| REL-003  | Reliability | STORY-091 | Lifecycle reliability checklist completed |
| REL-004  | Reliability | STORY-092 | DoS simulation mitigated; service responsive |
| REL-005  | Reliability | STORY-093 | Injection attempt blocked; no code execution |
| REL-006  | Reliability | STORY-094 | Placement scan shows no forbidden co-residency |
| REL-007  | Reliability | STORY-095 | Brute force/auth anomalies rate limited & alerted |
| REL-008  | Reliability | STORY-096 | MITM attempt fails; pinned cert validation passes |
| REL-009  | Reliability | STORY-097 | Iframe embed blocked; headers verified |
| REL-010  | Reliability | STORY-098 | Batch suspend/resume preserves data integrity |
| REL-011  | Reliability | STORY-099 | Unhealthy node auto-replaced; workload continues |
| REL-012  | Reliability | STORY-100 | Single node removal shows stable perf & zero data loss |
| REL-013  | Reliability | STORY-101 | Tier failure graceful degradation & recovery evidenced |
| REL-014  | Reliability | STORY-102 | External outage shows fallback & user messaging |
| REL-015  | Reliability | STORY-103 | LB failure retains sessions & continues routing |
| REL-016  | Reliability | STORY-104, STORY-177 | Server error shows logout/message per spec |
| REL-017  | Reliability | STORY-105 | Restore drill meets RPO/RTO & ransomware defenses |
| COMP-001 | Compatibility | STORY-106 | Published OS/browser list matches warranted spec |
| COMP-002 | Compatibility | STORY-107 | MFA (CIS2) succeeds across supported platforms |
| COMP-003 | Compatibility | STORY-108 | ≥90% critical journeys test pass per platform |
| OBS-002  | Observability | STORY-109 | Authenticated remote health dashboard accessible |
| OBS-003  | Observability | STORY-110 | Health event visible ≤60s after failure |
| OBS-004  | Observability | STORY-111 | Automated maintenance tasks executed; zero manual interventions |
| OBS-006  | Observability | STORY-112 | Remote performance dashboard matches local view |
| OBS-007  | Observability | STORY-113 | Performance metrics latency ≤60s |
| OBS-009  | Observability | STORY-114 | Endpoint latency histograms with p50/p95/p99 |
| OBS-010  | Observability | STORY-115 | Aggregate latency panel accurate within 2% roll-up |
| OBS-012  | Observability | STORY-116 | Error percentage metric & alert configured |
| OBS-014  | Observability | STORY-117 | Infra log entries include required fields |
| OBS-015  | Observability | STORY-118 | Retention policy enforced & reported |
| OBS-016  | Observability | STORY-119 | SIEM forwarding delivers test event <60s |
| OBS-017  | Observability | STORY-120 | All log levels supported; dynamic change works |
| OBS-018  | Observability | STORY-121 | Log level propagation <2min with alert on breach |
| OBS-020  | Observability | STORY-122 | Operations logs reconstruct workflow |
| OBS-021  | Observability | STORY-123 | Operational events include transaction_id |
| OBS-023  | Observability | STORY-124 | Audit events share transaction_id & ordered timestamps |
| OBS-025  | Observability | STORY-125 | Alerts delivered to multi-channel with context |
| OBS-027  | Observability | STORY-126 | Analytics outage non-impacting to transactions |
| OBS-029  | Observability | STORY-127 | Dashboard freshness age ≤60s |
| OBS-031  | Observability | STORY-128 | Anonymised behaviour metrics collected without identifiers |
| ACC-001  | Accessibility | STORY-129 | WCAG 2.2 AA scan & manual audit pass |
| ACC-002  | Accessibility | STORY-130 | Automated scans run across critical pages & browsers |
| ACC-003  | Accessibility | STORY-131 | Manual accessibility test executed per release |
| ACC-004  | Accessibility | STORY-132 | Defects tracked with parity priority & SLA |
| ACC-005  | Accessibility | STORY-133 | Tooling operational in dev/int/reference envs |
| ACC-006  | Accessibility | STORY-134 | Assistive tech not blocked by headers/CSP |
| ACC-007  | Accessibility | STORY-135 | Test dataset covers tables/forms/status messages |
| ACC-008  | Accessibility | STORY-136 | CI job executes accessibility scan step |
| ACC-009  | Accessibility | STORY-137 | Keyboard tab order regression test passes |
| ACC-010  | Accessibility | STORY-138 | Focus trap tests pass for modals/overlays |
| ACC-011  | Accessibility | STORY-139 | Screen reader ARIA role announcements verified |
| ACC-012  | Accessibility | STORY-140 | Accessibility results documented with feature tests |
| ACC-013  | Accessibility | STORY-141 | Central issue log maintained & current |
| ACC-014  | Accessibility | STORY-142 | Accessibility champion/workgroup active |
| ACC-015  | Accessibility | STORY-143 | Monthly accessibility report published |
| ACC-016  | Accessibility | STORY-144 | Exception process documented & used |
| ACC-017  | Accessibility | STORY-145 | Exception record contains required fields |
| ACC-018  | Accessibility | STORY-146 | Pre-commit checks complete <30s |
| ACC-019  | Accessibility | STORY-147 | CI accessibility stage completes <5min |
| ACC-020  | Accessibility | STORY-148 | Overnight full scan duration <2h |
| ACC-021  | Accessibility | STORY-149 | Accessibility regression triggers alert |
| ACC-022  | Accessibility | STORY-150 | False positive ratio report shows improvement |
| GOV-001  | Governance | STORY-151, STORY-185 | Service Management pre-live acceptance signed |
| GOV-002  | Governance | STORY-152, STORY-185 | Well-Architected review completed & actions closed |
| GOV-003  | Governance | STORY-153, STORY-185 | Solution Architecture Framework assessment approved |
| GOV-004  | Governance | STORY-154, STORY-185 | Engineering Red-lines compliance checklist signed |
| GOV-005  | Governance | STORY-155, STORY-185 | GDPR compliance assessment signed by IG |
| GOV-006  | Governance | STORY-156, STORY-185 | Medical Device out-of-scope statement recorded |
| GOV-007  | Governance | STORY-157, STORY-185 | FtRS Architects review & approval logged |
| GOV-008  | Governance | STORY-158, STORY-185 | Cloud Expert deployment approval documented |
| GOV-009  | Governance | STORY-159, STORY-185 | Solution Assurance approval ticket closed |
| GOV-010  | Governance | STORY-160, STORY-185 | Clinical Safety assurance approval recorded |
| GOV-011  | Governance | STORY-161, STORY-185 | Information Governance approval recorded |
| GOV-012  | Governance | STORY-162, STORY-185 | TRG approval session outcome logged |
| GOV-013  | Governance | STORY-163, STORY-185 | SIRO sign-off obtained |
| GOV-014  | Governance | STORY-164, STORY-185 | Caldicott Guardian approval recorded |
| GOV-015  | Governance | STORY-165, STORY-185 | DUEC Assurance Board acceptance logged |
| GOV-016  | Governance | STORY-166, STORY-185 | Live Services Board go-live approval recorded |
| PERF-002 | Performance | STORY-167, STORY-180 | Performance pillar checklist completed & actions closed |
| PERF-003 | Performance | STORY-168, STORY-176, STORY-178, STORY-180 | Performance expectations table versioned & referenced |
| PERF-004 | Performance | STORY-169, STORY-180 | Anonymised live-like dataset present & audited |
| PERF-005 | Performance | STORY-170, STORY-180 | Automated test suite matches defined actions & exclusions |
| PERF-006 | Performance | STORY-171, STORY-184 | Batch window p95 latency delta ≤5% |
| PERF-007 | Performance | STORY-172, STORY-179, STORY-183 | Telemetry overhead within CPU & latency thresholds |
| PERF-008 | Performance | STORY-173, STORY-184 | 8h rolling window p95 variance ≤10% |
| PERF-009 | Performance | STORY-174, STORY-180, STORY-184 | Regression alert triggers on >10% p95 increase |
| PERF-010 | Performance | STORY-175, STORY-180 | Percentile methodology document & tool config aligned |

> Add new rows as NFRs are formalised. Keep codes immutable.
