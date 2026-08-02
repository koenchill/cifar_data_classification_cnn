# Student Guide (source of truth for Release A)

Canonical copy of the course instructions used for guide-compliance. Implementation must match Steps 1–7 exactly; enterprise layers are additive only.

## 1. Why Image Classification is Important in Data Science?

Image classification is a critical task in computer vision, one of the most important applications of data science. Mastering it gives you the foundation to understand more complex topics, such as object detection, image segmentation, and even deep learning techniques like GANs (Generative Adversarial Networks).

## 2. Tools and Libraries Required

- VS Code: The code editor for writing Python scripts.
- Python: The programming language used to develop the model.
- Libraries:
  - PyTorch: A powerful deep learning library used to build the CNN.
  - Torchvision: A library for accessing and transforming image datasets.
  - Matplotlib: A visualization library for plotting images and results.

Installation:

```bash
pip install torch torchvision matplotlib
```

## 3. Step-by-Step Project Guide

### Step 1: Load and Preprocess the Dataset

- Use `torchvision.datasets.CIFAR10` to load CIFAR-10.
- Use `DataLoader` for train/test batches.
- Apply `ToTensor()` and `Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))`.
- Train: `root='./data'`, `train=True`, `download=True`, `batch_size=32`, `shuffle=True`.
- Test: `train=False`, `batch_size=32`, `shuffle=False`.

### Step 2: Define the CNN (`SimpleCNN`)

- `Conv2d(3, 32, 3, padding=1)` → ReLU → `MaxPool2d(2, 2)`
- `Conv2d(32, 64, 3, padding=1)` → ReLU → pool
- `Conv2d(64, 64, 3, padding=1)` → ReLU → pool
- Flatten `64 * 4 * 4`
- `Linear(64 * 4 * 4, 64)` → ReLU → `Linear(64, 10)` (logits)

### Step 3: Loss and Optimizer

- `nn.CrossEntropyLoss()`
- `optim.Adam(net.parameters(), lr=0.001)`

### Step 4: Training

- 10 epochs
- Per batch: `zero_grad` → forward → loss → `backward` → `step`
- Print loss every 100 mini-batches
- **Defect in guide snippet:** `running_loss` is printed but never accumulated — implementation must use `running_loss += loss.item()` then print `running_loss / 100` and reset.

### Step 5: Evaluating

- `torch.no_grad()`
- `torch.max(outputs, 1)` for predicted class
- Report accuracy on **10,000** test images

### Step 6: Visualize

- Unnormalize with `img / 2 + 0.5`
- Display **8** test images with **Actual** and **Predicted** labels
- Guide uses undefined `classes` — use official CIFAR-10 class names

### Step 7: Save the Model

- `torch.save(net.state_dict(), 'cnn_model.pth')`
- Repo also stores `models/cnn_model.pth` (see `GUIDE_TRACEABILITY.md`)

## 4. Why This Project is Important for Data Science

Image classification is integral when dealing with visual data. Mastering it enables advanced tasks (object detection, segmentation, video analysis) and matters in healthcare, automotive, and retail.

## 5. Tough Questions for Students

Full list (20) is in [`guide_tough_questions_source.md`](guide_tough_questions_source.md). Phase 5 answers them in `guide_questions.md`.
