"""Generate formal technical leadership Word briefing."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


def main() -> Path:
    out = Path("docs/evidence/leadership_brief_cifar_cnn_revB.docx")
    out.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Technical Leadership Briefing")
    run.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = subtitle.add_run(
        "CIFAR-10 Convolutional Neural Network Classification Platform"
    )
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    m = meta.add_run(
        f"Status Update  |  {date.today().isoformat()}  |  Classification: Internal  |  Rev. B"
    )
    m.font.size = Pt(10)
    m.italic = True
    m.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

    doc.add_paragraph()

    def add_heading_custom(text: str) -> None:
        p = doc.add_paragraph()
        hr = p.add_run(text)
        hr.bold = True
        hr.font.size = Pt(13)
        hr.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)

    def add_body(text: str) -> None:
        p = doc.add_paragraph(text)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15

    def add_bullet(text: str) -> None:
        p = doc.add_paragraph(text, style="List Bullet")
        p.paragraph_format.space_after = Pt(3)

    add_heading_custom("1. Purpose of Project")
    add_body(
        "This initiative delivers an end-to-end, governed reference platform for "
        "CIFAR-10 image classification: data loading, model training, rigorous "
        "evaluation, model packaging, and authenticated inference serving, supported "
        "by CI, application-security scanning, and GitOps-ready deployment patterns."
    )
    add_body(
        "The dataset is the standard CIFAR-10 corpus of 60,000 labeled 32×32 color "
        "images (50,000 training / 10,000 locked official test). The program is "
        "educational and architectural in nature; reported accuracy is not a claim "
        "of production performance on arbitrary real-world photography."
    )

    add_heading_custom("2. Under the Hood — Foundational CNN Concepts")
    add_body(
        "A convolutional neural network (CNN) learns hierarchical visual features "
        "directly from pixels. The following mechanisms are central to the current "
        "training stack:"
    )
    add_bullet(
        "Representation: each image is converted to a normalized tensor suitable "
        "for gradient-based learning."
    )
    add_bullet(
        "Convolution and pooling: learned filters detect local patterns (edges, "
        "textures, parts); pooling reduces spatial resolution and improves "
        "translation tolerance."
    )
    add_bullet(
        "Nonlinearity (ReLU): enables composition of complex, non-linear decision "
        "boundaries across layers."
    )
    add_bullet(
        "Classification head: spatial features are flattened and mapped to ten "
        "class logits (airplane, automobile, bird, cat, deer, dog, frog, horse, "
        "ship, truck)."
    )
    add_bullet(
        "Optimization (current best CPU recipe): ImprovedCNN with BatchNorm and "
        "Dropout; train-only augmentation (crop, flip, color jitter, Cutout/"
        "RandomErasing); AdamW with weight decay; label smoothing; cosine "
        "learning-rate annealing; early stopping on a locked 45K/5K validation "
        "split drawn only from the training pool."
    )
    add_bullet(
        "Evaluation discipline: the official 10K test set is reserved for final "
        "reporting (accuracy, precision, recall, F1, confusion, one-vs-rest "
        "ROC-AUC). Optional horizontal-flip test-time augmentation (TTA) averages "
        "softmax probabilities at inference without retraining."
    )

    add_heading_custom(
        "3. Metrics (Official Locked Test Set — 10,000 Images)"
    )
    add_body(
        "Results below are computed on the official CIFAR-10 test split. Macro "
        "metrics average per-class precision, recall, and F1. Macro ROC-AUC "
        "summarizes one-vs-rest ranking quality. Figures reflect the latest "
        "rigorous evaluation artifacts."
    )

    table = doc.add_table(rows=5, cols=6)
    table.style = "Table Grid"
    headers = [
        "Model / Recipe",
        "Accuracy",
        "Macro P",
        "Macro R",
        "Macro F1",
        "ROC-AUC",
    ]
    data_rows = [
        [
            "Baseline SimpleCNN (10 epochs, no augmentation)",
            "73.4%",
            "0.740",
            "0.734",
            "0.736",
            "0.963",
        ],
        [
            "ImprovedCNN + basic augmentation (prior best)",
            "78.5%",
            "0.783",
            "0.785",
            "0.783",
            "0.976",
        ],
        [
            "ImprovedCNN boost (Cutout + cosine + AdamW/WD + label smooth)",
            "80.8%",
            "0.807",
            "0.808",
            "0.806",
            "0.979",
        ],
        [
            "ImprovedCNN boost + TTA (horizontal flip)",
            "81.8%",
            "0.817",
            "0.818",
            "0.817",
            "0.981",
        ],
    ]
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for paragraph in cell.paragraphs:
            for cell_run in paragraph.runs:
                cell_run.bold = True
                cell_run.font.size = Pt(9)
    for r_idx, row in enumerate(data_rows, start=1):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx].cells[c_idx]
            cell.text = val
            for paragraph in cell.paragraphs:
                for cell_run in paragraph.runs:
                    cell_run.font.size = Pt(9)

    doc.add_paragraph()
    add_body(
        "Interpretation: the CPU boost stack improved locked-test accuracy from "
        "73.4% (baseline) to 80.8%, and to 81.8% with TTA—an absolute gain of "
        "approximately 8.4 percentage points. Macro precision, recall, F1, and "
        "ROC-AUC moved in the same direction. Vehicle classes remain strongest; "
        "cat and bird remain the primary residual error modes."
    )

    add_heading_custom("4. Current Risks and Blockers")
    add_bullet(
        "Accuracy ceiling on CPU: ImprovedCNN is approaching practical limits for "
        "this topology (~low-80s). Crossing ~90% still requires GPU-backed "
        "ResNet18 (or similar) transfer learning."
    )
    add_bullet(
        "Transfer learning paused: a CPU-only ResNet18 ImageNet transfer run was "
        "halted due to excessive wall-clock time; the pipeline and configs remain "
        "ready pending GPU capacity."
    )
    add_bullet(
        "AI risk (AIR-01): CIFAR-10 scores must not be over-interpreted as "
        "real-world vision performance."
    )
    add_bullet(
        "Security residuals (CYB-07 / CYB-08): accepted SCA/CVE allowlist items "
        "require tracked upgrades before any production posture claim."
    )
    add_bullet(
        "Champion discipline: continue selecting on validation only; publish "
        "official test metrics once per candidate to avoid leakage."
    )

    add_heading_custom("5. Next Steps")
    add_bullet(
        "Treat artifacts/improved_boost/model_best.pth (with optional TTA at "
        "serve/eval time) as the current CPU champion candidate for packaging."
    )
    add_bullet(
        "Decide compute path: provision GPU (local NVIDIA, Colab, or cloud GPU) "
        "to execute the existing two-stage ResNet18 transfer workflow targeting "
        "~90–94% test accuracy."
    )
    add_bullet(
        "If GPU is approved, pair transfer with cosine/OneCycle scheduling and "
        "stronger augmentation; report locked-test P/R/F1/ROC once after "
        "validation-based selection."
    )
    add_bullet(
        "Maintain governed serving/GitOps path for the selected bundle; keep "
        "educational/non-production positioning explicit in external "
        "communications."
    )

    add_heading_custom("Executive Summary")
    add_body(
        "Platform Releases A–E establish a governed train–evaluate–serve path. "
        "Live model quality on the locked CIFAR-10 test set has advanced from "
        "approximately 73% (guide baseline) to 80.8% with the ImprovedCNN boost "
        "recipe, and to 81.8% with test-time augmentation. Material further gains "
        "toward the high-90s require GPU-backed transfer learning; until then, "
        "the boost checkpoint is the recommended CPU reference model."
    )

    footer = doc.add_paragraph()
    footer.paragraph_format.space_before = Pt(18)
    fr = footer.add_run(
        "Document owner: Model / Platform Engineering  ·  Distribution: Technical "
        "Leadership  ·  Evidence: artifacts/baseline_rigorous, "
        "artifacts/improved_full_rigorous_latest, "
        "artifacts/improved_boost_rigorous, "
        "artifacts/improved_boost_rigorous_tta  ·  Checkpoint: "
        "artifacts/improved_boost/model_best.pth"
    )
    fr.font.size = Pt(9)
    fr.italic = True
    fr.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

    doc.save(out)
    return out.resolve()


if __name__ == "__main__":
    print(main())
