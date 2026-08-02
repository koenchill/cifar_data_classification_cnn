# RACI and Ownership

Single-owner portfolio project: primary owner is **koenchill**. Roles below are assigned for control traceability; the same person may hold multiple roles until a team expands. Separation of duties is **aspirational** for local demo and **required** for production promotion evidence (Phase 17).

## Role assignments

| Role | Owner | Notes |
|---|---|---|
| AI system owner | koenchill | Intended use, overall acceptance |
| Model owner | koenchill | Architecture, champion selection |
| Data owner | koenchill | CIFAR-10 lineage, splits |
| Application owner | koenchill | FastAPI service |
| Platform owner | koenchill | Terraform / EKS / Argo |
| Security owner | koenchill | Threat model, IAM, scanning |
| SRE / operations owner | koenchill | SLOs, runbooks, incidents |
| Privacy / legal reviewer | koenchill (interim) | Reassign if personal data scope expands |
| Final release approver | koenchill | Signs Release E decision |

## RACI (selected activities)

| Activity | AI sys | Model | Data | App | Platform | Security | SRE | Approver |
|---|---|---|---|---|---|---|---|---|
| Intended use / boundary | A | C | C | C | C | C | I | A |
| Guide baseline (Release A) | I | A | C | C | I | C | I | I |
| Champion / bundle gate | C | A | C | C | I | C | I | A |
| API security controls | C | I | I | A | C | A | C | I |
| Terraform / EKS apply | I | I | I | C | A | A | C | C |
| Prod GitOps promote | C | C | I | C | A | A | A | A |
| Incident response | C | C | I | C | C | A | A | I |
| Model retirement | A | A | C | C | C | C | C | A |

Legend: R = Responsible, A = Accountable, C = Consulted, I = Informed. Where one person holds multiple columns, the **Accountable** cell is the decision authority for that activity.

## Approval authority

- **Phase / release exit gates:** Final release approver (with security + model consult for C+).  
- **Risk acceptance:** Named owner in risk register; high AI/security risks require AI system owner + security owner.  
- **Exceptions:** Time-bounded; recorded in risk register with expiry.
