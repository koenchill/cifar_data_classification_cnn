"""Generate formal technical leadership Word briefing."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


def _load_summary(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _fmt_pct(x: float) -> str:
    return f"{100.0 * x:.1f}%"


def _fmt3(x: float) -> str:
    return f"{x:.3f}"


def main() -> Path:
    out = Path("docs/evidence/leadership_brief_cifar_cnn_revD.docx")
    out.parent.mkdir(parents=True, exist_ok=True)

    baseline = _load_summary("artifacts/baseline_rigorous/summary.json")
    improved = _load_summary("artifacts/improved_full_rigorous_latest/summary.json")
    boost = _load_summary("artifacts/improved_boost_rigorous/summary.json")
    boost_tta = _load_summary("artifacts/improved_boost_rigorous_tta/summary.json")

    transfer_summary_path = Path("artifacts/transfer_rigorous/summary.json")
    transfer_tta_path = Path("artifacts/transfer_rigorous_tta/summary.json")
    if transfer_tta_path.is_file():
        transfer = _load_summary(str(transfer_tta_path))
    elif transfer_summary_path.is_file():
        transfer = _load_summary(str(transfer_summary_path))
    else:
        transfer = None

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
        f"Status Update  |  {date.today().isoformat()}  |  Classification: Internal  |  Rev. D"
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

    def fill_header(table, headers: list[str]) -> None:
        for i, h in enumerate(headers):
            cell = table.rows[0].cells[i]
            cell.text = h
            for paragraph in cell.paragraphs:
                for cell_run in paragraph.runs:
                    cell_run.bold = True
                    cell_run.font.size = Pt(9)

    def fill_row(table, r_idx: int, values: list[str]) -> None:
        for c_idx, val in enumerate(values):
            cell = table.rows[r_idx].cells[c_idx]
            cell.text = val
            for paragraph in cell.paragraphs:
                for cell_run in paragraph.runs:
                    cell_run.font.size = Pt(9)

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
        "Current delivery uses two complementary stacks after the Colab GPU switch:"
    )
    add_bullet(
        "CPU champion (ImprovedCNN): BatchNorm/Dropout; train-only crop/flip/color "
        "jitter/Cutout; AdamW + weight decay; label smoothing; cosine LR; optional "
        "horizontal-flip TTA at evaluation."
    )
    add_bullet(
        "GPU transfer path (ResNet18CIFAR): ImageNet-pretrained residual backbone "
        "adapted for 32×32; two-stage fine-tune via scripts/train_transfer_live.py "
        "--device cuda on Google Colab (NVIDIA), because the primary workstation "
        "has AMD Radeon 780M graphics and cannot run CUDA."
    )
    add_bullet(
        "Evaluation discipline: tune on locked 45K/5K train/val from the training "
        "pool only; report once on the official 10K test set."
    )

    add_heading_custom(
        "3. Latest Locked-Test Metrics (Official 10,000 Images)"
    )
    add_body(
        "Source artifacts on workstation as of this revision. Aggregate metrics "
        "are from rigorous evaluation JSON summaries."
    )

    rows = [
        [
            "Baseline SimpleCNN",
            _fmt_pct(baseline["accuracy"]),
            _fmt3(baseline["macro_precision"]),
            _fmt3(baseline["macro_recall"]),
            _fmt3(baseline["macro_f1"]),
            _fmt3(baseline["roc_auc_macro"]),
        ],
        [
            "ImprovedCNN + basic aug",
            _fmt_pct(improved["accuracy"]),
            _fmt3(improved["macro_precision"]),
            _fmt3(improved["macro_recall"]),
            _fmt3(improved["macro_f1"]),
            _fmt3(improved["roc_auc_macro"]),
        ],
        [
            "ImprovedCNN boost",
            _fmt_pct(boost["accuracy"]),
            _fmt3(boost["macro_precision"]),
            _fmt3(boost["macro_recall"]),
            _fmt3(boost["macro_f1"]),
            _fmt3(boost["roc_auc_macro"]),
        ],
        [
            "ImprovedCNN boost + TTA (CPU champion)",
            _fmt_pct(boost_tta["accuracy"]),
            _fmt3(boost_tta["macro_precision"]),
            _fmt3(boost_tta["macro_recall"]),
            _fmt3(boost_tta["macro_f1"]),
            _fmt3(boost_tta["roc_auc_macro"]),
        ],
    ]
    if transfer is not None:
        label = "ResNet18CIFAR transfer"
        if transfer.get("tta_flip"):
            label += " + TTA"
        rows.append(
            [
                label,
                _fmt_pct(transfer["accuracy"]),
                _fmt3(transfer["macro_precision"]),
                _fmt3(transfer["macro_recall"]),
                _fmt3(transfer["macro_f1"]),
                _fmt3(transfer["roc_auc_macro"]),
            ]
        )
    else:
        rows.append(
            [
                "ResNet18CIFAR Colab GPU transfer",
                "Pending",
                "—",
                "—",
                "—",
                "—",
            ]
        )

    table = doc.add_table(rows=1 + len(rows), cols=6)
    table.style = "Table Grid"
    fill_header(
        table,
        ["Model / Recipe", "Accuracy", "Macro P", "Macro R", "Macro F1", "ROC-AUC"],
    )
    for i, row in enumerate(rows, start=1):
        fill_row(table, i, row)

    doc.add_paragraph()
    add_body(
        f"Current CPU champion (boost + TTA): accuracy {_fmt_pct(boost_tta['accuracy'])}, "
        f"macro P/R/F1 {_fmt3(boost_tta['macro_precision'])} / "
        f"{_fmt3(boost_tta['macro_recall'])} / {_fmt3(boost_tta['macro_f1'])}, "
        f"macro ROC-AUC {_fmt3(boost_tta['roc_auc_macro'])}, "
        f"ECE {_fmt3(boost_tta['ece'])}. Absolute gain vs baseline: "
        f"+{100.0 * (boost_tta['accuracy'] - baseline['accuracy']):.1f} percentage points."
    )

    add_heading_custom("3a. Per-Class P / R / F1 — CPU Champion (Boost + TTA)")
    pc = boost_tta["per_class"]
    pctable = doc.add_table(rows=1 + len(pc), cols=4)
    pctable.style = "Table Grid"
    fill_header(pctable, ["Class", "Precision", "Recall", "F1"])
    for i, (name, scores) in enumerate(pc.items(), start=1):
        fill_row(
            pctable,
            i,
            [
                name,
                _fmt3(scores["precision"]),
                _fmt3(scores["recall"]),
                _fmt3(scores["f1"]),
            ],
        )
    doc.add_paragraph()
    add_body(
        "Strongest classes: automobile, ship, truck. Weakest residual errors: "
        "cat (recall) and bird — primary targets for the ResNet transfer uplift."
    )

    add_heading_custom("4. Colab / GPU Switch Status")
    add_bullet(
        "Local workstation: AMD Radeon 780M; CUDA not available. CPU PyTorch retained."
    )
    add_bullet(
        "GPU execution path: Google Colab + notebooks/colab_transfer_gpu.ipynb."
    )
    add_bullet(
        "Code on GitHub: branch feature/live-rigorous-metrics-roc "
        "(scripts/train_transfer_live.py, transfer_stage*_gpu.yaml, --device cuda)."
    )
    if transfer is None:
        add_bullet(
            "ResNet metrics: not yet available on the workstation. "
            "artifacts/transfer_live/model_best.pth and "
            "artifacts/transfer_rigorous/summary.json were not present at brief "
            "generation. Colab must finish training and the .pth weights "
            "(not the .ipynb) must be downloaded before Rev E can publish "
            "transfer P/R/F1/ROC."
        )
    else:
        add_bullet(
            "ResNet transfer metrics included in Section 3 from local rigorous "
            "evaluation artifacts."
        )

    add_heading_custom("5. Current Risks and Blockers")
    add_bullet(
        "GPU/Colab completion risk: ~90%+ target blocked until valid ResNet "
        "weights are produced and evaluated."
    )
    add_bullet(
        "Artifact hygiene: prior downloads included notebook files named like "
        "model_best; only a true .pth state dict is valid for ResNet eval."
    )
    add_bullet(
        "AI risk (AIR-01): do not over-claim CIFAR scores as real-world vision performance."
    )
    add_bullet(
        "Security residuals (CYB-07 / CYB-08): SCA allowlist items remain tracked."
    )

    add_heading_custom("6. Next Steps")
    add_bullet(
        "Colab: BRANCH=feature/live-rigorous-metrics-roc; run "
        "train_transfer_live.py --device cuda; download model_best.pth."
    )
    add_bullet(
        "Local: evaluate_rigorous.py --live --model ResNet18CIFAR "
        "--normalize imagenet --tta; update brief to Rev E with transfer metrics."
    )
    add_bullet(
        "Until then, ship/demo with ImprovedCNN boost + TTA (81.8%) as CPU champion."
    )

    add_heading_custom("Executive Summary")
    if transfer is None:
        add_body(
            "Latest confirmed locked-test metrics remain the ImprovedCNN boost "
            f"stack: {_fmt_pct(boost['accuracy'])} without TTA and "
            f"{_fmt_pct(boost_tta['accuracy'])} with TTA (macro F1 "
            f"{_fmt3(boost_tta['macro_f1'])}, ROC-AUC "
            f"{_fmt3(boost_tta['roc_auc_macro'])}). The GPU strategy has switched "
            "to Colab because local hardware cannot run CUDA; ResNet18 transfer "
            "metrics will be published immediately after Colab weights are "
            "verified on the locked test set."
        )
    else:
        add_body(
            "Latest locked-test results include ResNet18 transfer metrics in "
            "Section 3. CPU boost + TTA remains "
            f"{_fmt_pct(boost_tta['accuracy'])}; compare against the transfer "
            "row for the new champion decision."
        )

    footer = doc.add_paragraph()
    footer.paragraph_format.space_before = Pt(18)
    fr = footer.add_run(
        "Document owner: Model / Platform Engineering  ·  Distribution: Technical "
        "Leadership  ·  Metrics sources: artifacts/baseline_rigorous, "
        "artifacts/improved_full_rigorous_latest, "
        "artifacts/improved_boost_rigorous, "
        "artifacts/improved_boost_rigorous_tta  ·  "
        "Branch: feature/live-rigorous-metrics-roc"
    )
    fr.font.size = Pt(9)
    fr.italic = True
    fr.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

    doc.save(out)
    return out.resolve()


if __name__ == "__main__":
    print(main())
