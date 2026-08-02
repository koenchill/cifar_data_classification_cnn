# Data Card — CIFAR-10 (baseline)

| Field | Value |
|---|---|
| Dataset | CIFAR-10 |
| Owner | Data owner (`koenchill`) |
| Phase | 2 |
| Status | Approved for educational / guide baseline use |

## Motivation / intended use

Benchmark image classification into 10 object categories for the student guide and controlled ML experiments. **Not** representative of enterprise production imagery.

## Composition

| Split | Size | Role |
|---|---|---|
| Official train | 50,000 | Training (+ stratified val indices) |
| Official test | 10,000 | Locked until final evaluation |
| Classes | 10 | airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck |

Images are 32×32 RGB.

## Collection / source

Loaded via `torchvision.datasets.CIFAR10` into `./data` (`download=True`). Citation: Krizhevsky (2009), *Learning Multiple Layers of Features from Tiny Images*.

## Preprocessing (guide contract)

```text
Compose([ToTensor(), Normalize((0.5,0.5,0.5), (0.5,0.5,0.5))])
```

- Train loader: `batch_size=32`, `shuffle=True`
- Test loader: `batch_size=32`, `shuffle=False`
- No augmentation on evaluation/test transforms

## Lineage / change control

See `cifar_cnn.data.lineage.build_lineage_record`. Dataset or split changes are **model-affecting** and require model + data owner review.

## Relevance and limitations (AI RMF Map)

- **Relevance:** Standard CV teaching benchmark; matches guide requirements.
- **Representativeness:** Low for real enterprise photos (resolution, domain, class ontology).
- **Known limitations:** Tiny images; class imbalance not a primary concern (balanced 10-way); no personal identity labels by design, but misuse for real-world claims is prohibited.
- **Mismatch vs enterprise imagery:** Different cameras, lighting, class set, and risk context — do not claim transfer without new evidence.

## Prohibited inference claims

- Real-world accuracy or safety guarantees  
- Use as medical, automotive control, or identity verification signal  
