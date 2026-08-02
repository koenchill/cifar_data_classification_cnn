# Threat and Abuse-Case Model

| Field | Value |
|---|---|
| Method | STRIDE-informed + AI abuse cases |
| Scope | Guide baseline through enterprise API/EKS path |
| Status | Phase 0 baseline; revise at Phases 10–12 and 16 |

## Assets

- Model weights and bundles  
- Inference API availability and integrity  
- OIDC tokens / cloud credentials / Terraform state  
- Audit evidence and release provenance  
- CIFAR-10 lineage / split integrity (scientific integrity)

## STRIDE summary

| Category | Example threat | Treatment direction |
|---|---|---|
| Spoofing | Stolen OIDC token calls predict | Short-lived tokens; audience/issuer checks; revoke |
| Tampering | Altered weights or unsigned image | Hash/sign; admission by digest; fail closed |
| Repudiation | Unaudited predictions | Structured audit without secrets/pixels |
| Information disclosure | Secrets in git/logs; model exfil | Secret scan; redaction; rate limits; least privilege |
| Denial of service | Flood `/v1/predict` with huge images | Rate/size/decompress limits; timeouts; HPA bounds |
| Elevation of privilege | CI apply prod; over-broad IAM | Separated OIDC roles; negative IAM tests; AppProjects |

## AI / ML abuse cases

| ID | Abuse / failure | Impact | Phase controls |
|---|---|---|---|
| AI-01 | Overclaim real-world performance | Misleading users | Intended-use docs; model card limits |
| AI-02 | Test-set leakage / tuning on test | Invalid metrics | Locked test; leakage tests (Phase 2+) |
| AI-03 | Adversarial or OOD high-confidence wrong labels | Bad decisions if misused | Robustness Measure; uncertain flags (Phase 8/11) |
| AI-04 | Malicious image bombs / decompress | API DoS / RCE risk | Input security (Phase 11) |
| AI-05 | Supply-chain poisoned deps/base image | Compromised train/serve | Pin/scan/sign (Phases 1, 12) |
| AI-06 | Unauthorized model swap in cluster | Silent behavior change | Signed digest + Argo + admission (15) |

## Trust assumptions

- CIFAR-10 from Torchvision is integrity-acceptable for education; still record lineage.  
- Local Docker demo may omit full EKS controls but must not be labeled equivalent.  
- Production requires OIDC, RBAC, rate limits, audit (mandatory, not backlog).

## Residual risk statement

Educational offline use: accepted by AI system owner.  
Public/production API: not accepted until Releases C–E exit gates and named residual-risk acceptances are recorded.
