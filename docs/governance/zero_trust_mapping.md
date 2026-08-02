# Zero Trust Target Mapping

Mapped to identity, workload, network, application, data, visibility, automation, and governance. Local Docker demo may meet a subset; **production EKS path** targets the maturity below.

## Pillars

| Pillar | Target control | Min production maturity |
|---|---|---|
| Identity | OIDC for humans and workloads; no shared long-lived admin | Enforced for API and Argo SSO |
| Workload / device | Non-root containers; PSS restricted; signed digests | Enforced admission |
| Network | Default-deny NetworkPolicies; private nodes; controlled egress | Enforced in app namespaces |
| Application | RBAC deny-by-default; rate limits; input bounds | Enforced on predict path |
| Data | Encrypted state/ECR/volumes; no secrets in git; redacted logs | Enforced |
| Visibility | Audit logs, metrics, alerts for authz/SLO/policy | Dashboards + paging for critical |
| Automation | CI OIDC roles; Argo reconcile; policy-as-code | CI cannot cluster-admin apply |
| Governance | Intended use, RACI, risk acceptance, release gates | Signed ORR before prod |

## Environment expectations

| Environment | Zero Trust bar |
|---|---|
| Local train/eval | Secrets hygiene + intended-use honesty |
| Local Docker demo | TLS optional for lab; auth strongly preferred; never claim prod equivalence |
| Staging | Full control set with smaller capacity |
| Production | Full set + approvals + signed digest only |

## Explicit non-goals for early phases

- Device posture agents on student laptops  
- Hardware-backed attestation for training jobs  
These may be deferred without blocking Release A.
