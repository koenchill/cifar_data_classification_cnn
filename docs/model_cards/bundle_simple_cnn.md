# Model Card — Governed Bundle `simple_cnn-1.0.x`

| Field | Value |
|---|---|
| Bundle id | `simple_cnn` |
| Champion | `simple_cnn_baseline` |
| Formats | `model.pt` (state_dict), `model.onnx` (opset 17) |
| Integrity | SHA-256 file hashes + HMAC-SHA256 `manifest.sig` |
| Status | Release B candidate — **non-production** |

## Contents

- `metadata.json` — class order, normalization, constraints, limitations, identities  
- `classes.json` — official CIFAR-10 names  
- `bom.json` — CycloneDX-like stub  

- `manifest.json` / `manifest.sig` — hashed inventory + signature  

## Serving constraints

- Input: NCHW float32, dynamic batch, 3×32×32  
- Output: logits (10)  
- Apply guide Normalize((0.5,)×3, (0.5,)×3) unless metadata overridden  

## Integrity ops

```text
verify_bundle("models/bundles/simple_cnn-1.0.1")
rollback_bundle("models/bundles", "simple_cnn-1.0.0")
```

Production signing must replace the HMAC key with a managed secret / cosign (Release C+).
