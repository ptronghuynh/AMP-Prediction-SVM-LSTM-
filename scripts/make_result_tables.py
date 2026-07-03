"""Create result tables and preserve manuscript figure files."""

from __future__ import annotations

import csv
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

from compute_confidence_intervals import hanley_mcneil_auc_ci, wilson_ci

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"
FIGURES_DIR = REPO_ROOT / "figures"


def fmt(value: float | str, digits: int = 4) -> str:
    if isinstance(value, str):
        return value
    return f"{value:.{digits}f}"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def class_metrics(tn: int, fp: int, fn: int, tp: int) -> list[dict[str, str]]:
    support0 = tn + fp
    support1 = tp + fn
    total = support0 + support1
    precision0 = tn / (tn + fn)
    recall0 = tn / (tn + fp)
    f10 = 2 * precision0 * recall0 / (precision0 + recall0)
    precision1 = tp / (tp + fp)
    recall1 = tp / (tp + fn)
    f11 = 2 * precision1 * recall1 / (precision1 + recall1)
    accuracy = (tn + tp) / total
    macro_precision = (precision0 + precision1) / 2
    macro_recall = (recall0 + recall1) / 2
    macro_f1 = (f10 + f11) / 2
    weighted_precision = (precision0 * support0 + precision1 * support1) / total
    weighted_recall = (recall0 * support0 + recall1 * support1) / total
    weighted_f1 = (f10 * support0 + f11 * support1) / total
    return [
        {
            "class": "Non-AMP (0)",
            "precision": fmt(precision0),
            "recall": fmt(recall0),
            "f1_score": fmt(f10),
            "support": str(support0),
        },
        {
            "class": "AMP (1)",
            "precision": fmt(precision1),
            "recall": fmt(recall1),
            "f1_score": fmt(f11),
            "support": str(support1),
        },
        {
            "class": "accuracy",
            "precision": "",
            "recall": "",
            "f1_score": fmt(accuracy),
            "support": str(total),
        },
        {
            "class": "macro avg",
            "precision": fmt(macro_precision),
            "recall": fmt(macro_recall),
            "f1_score": fmt(macro_f1),
            "support": str(total),
        },
        {
            "class": "weighted avg",
            "precision": fmt(weighted_precision),
            "recall": fmt(weighted_recall),
            "f1_score": fmt(weighted_f1),
            "support": str(total),
        },
    ]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_text_center(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: str, fnt) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - (box[2] - box[0]) / 2, xy[1] - (box[3] - box[1]) / 2), text, fill=fill, font=fnt)


def save_confusion_matrix(path: Path, title: str, matrix: list[list[int]]) -> None:
    width, height = 920, 760
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title_font = font(30, True)
    label_font = font(22, True)
    cell_font = font(30, True)
    small_font = font(18)

    draw_text_center(draw, (width // 2, 50), title, "#1f2937", title_font)
    x0, y0, cell = 210, 160, 220
    labels = ["Pred non-AMP", "Pred AMP"]
    rows = ["True non-AMP", "True AMP"]
    max_value = max(max(row) for row in matrix)
    for j, label in enumerate(labels):
        draw_text_center(draw, (x0 + j * cell + cell // 2, y0 - 35), label, "#111827", small_font)
    for i, row_label in enumerate(rows):
        draw_text_center(draw, (x0 - 80, y0 + i * cell + cell // 2), row_label, "#111827", small_font)
        for j, value in enumerate(matrix[i]):
            intensity = int(235 - 130 * (value / max_value))
            fill = (intensity, min(245, intensity + 20), 255)
            rect = [x0 + j * cell, y0 + i * cell, x0 + (j + 1) * cell, y0 + (i + 1) * cell]
            draw.rectangle(rect, fill=fill, outline="#1f2937", width=3)
            draw_text_center(draw, (rect[0] + cell // 2, rect[1] + cell // 2), f"{value:,}", "#111827", cell_font)
    draw_text_center(draw, (width // 2, height - 70), "Balanced held-out test set: 3,000 AMP and 3,000 non-AMP records", "#374151", label_font)
    image.save(path)


def save_ci_plot(path: Path, title: str, rows: list[dict[str, str]], y_min: float, y_max: float) -> None:
    width, height = 1100, 760
    left, right, top, bottom = 120, 70, 95, 120
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title_font = font(30, True)
    axis_font = font(18)
    label_font = font(20, True)
    draw_text_center(draw, (width // 2, 45), title, "#111827", title_font)
    plot_w, plot_h = width - left - right, height - top - bottom
    draw.line((left, top, left, top + plot_h), fill="#111827", width=2)
    draw.line((left, top + plot_h, left + plot_w, top + plot_h), fill="#111827", width=2)

    def y_to_px(y: float) -> int:
        return int(top + plot_h - (y - y_min) / (y_max - y_min) * plot_h)

    ticks = 5
    for idx in range(ticks + 1):
        y = y_min + (y_max - y_min) * idx / ticks
        yp = y_to_px(y)
        draw.line((left - 8, yp, left + plot_w, yp), fill="#e5e7eb", width=1)
        draw.text((25, yp - 10), f"{y:.2f}", fill="#374151", font=axis_font)

    n = len(rows)
    colors_local = ["#2563eb", "#059669", "#dc2626", "#7c3aed", "#ea580c", "#0891b2"]
    for idx, row in enumerate(rows):
        x = int(left + plot_w * (idx + 0.5) / n)
        acc = float(row["accuracy"])
        low = float(row["accuracy_ci_low"])
        high = float(row["accuracy_ci_high"])
        y = y_to_px(acc)
        y_low = y_to_px(low)
        y_high = y_to_px(high)
        draw.line((x, y_high, x, y_low), fill="#111827", width=4)
        draw.line((x - 12, y_high, x + 12, y_high), fill="#111827", width=3)
        draw.line((x - 12, y_low, x + 12, y_low), fill="#111827", width=3)
        color = colors_local[idx % len(colors_local)]
        draw.ellipse((x - 13, y - 13, x + 13, y + 13), fill=color, outline="#111827", width=2)
        label = row.get("model") or row.get("dataset") or ""
        draw_text_center(draw, (x, top + plot_h + 35), label.replace("-combined", ""), "#111827", label_font)
        draw_text_center(draw, (x, y - 35), f"{acc:.4f}", "#111827", axis_font)
    image.save(path)


def flow_pdf(path: Path, title: str, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = landscape(letter)
    c = canvas.Canvas(str(path), pagesize=landscape(letter))
    c.setTitle(title)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(page_w / 2, page_h - 45, title)
    box_w, box_h = 140, 54
    for row_idx, row in enumerate(rows):
        count = len(row)
        gap = (page_w - 90 - count * box_w) / max(count - 1, 1)
        y = page_h - 135 - row_idx * 120
        for idx, label in enumerate(row):
            x = 45 + idx * (box_w + gap)
            c.setFillColor(colors.HexColor("#eff6ff"))
            c.setStrokeColor(colors.HexColor("#1f2937"))
            c.roundRect(x, y, box_w, box_h, 8, fill=1, stroke=1)
            c.setFillColor(colors.HexColor("#111827"))
            c.setFont("Helvetica-Bold", 9)
            lines = label.split("\n")
            for line_idx, line in enumerate(lines):
                c.drawCentredString(x + box_w / 2, y + box_h / 2 + 7 - 12 * line_idx, line)
            if idx < count - 1:
                c.setStrokeColor(colors.HexColor("#374151"))
                c.line(x + box_w + 5, y + box_h / 2, x + box_w + gap - 8, y + box_h / 2)
                c.line(x + box_w + gap - 8, y + box_h / 2, x + box_w + gap - 18, y + box_h / 2 + 5)
                c.line(x + box_w + gap - 8, y + box_h / 2, x + box_w + gap - 18, y + box_h / 2 - 5)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#4b5563"))
    c.save()


def create_if_missing(path: Path, maker, *args) -> None:
    """Create a figure file only when it is absent."""
    if path.exists():
        return
    maker(path, *args)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    svm_cm = {"tn": 2940, "fp": 60, "fn": 120, "tp": 2880}
    lstm_cm = {"tn": 2880, "fp": 120, "fn": 150, "tp": 2850}

    fields_report = ["class", "precision", "recall", "f1_score", "support"]
    write_csv(RESULTS_DIR / "table2_svm_classification_report.csv", class_metrics(**svm_cm), fields_report)
    write_csv(RESULTS_DIR / "table3_lstm_classification_report.csv", class_metrics(**lstm_cm), fields_report)

    internal_specs = [
        {
            "model": "SVM-combined",
            "test_n": 6000,
            "correct": 5820,
            "accuracy": 0.9700,
            "macro_precision": 0.9700,
            "macro_recall": 0.9700,
            "macro_f1": 0.9700,
            "approx_errors": 180,
            "note": "AUC-ROC 0.9962 is reported with the SVM classification results.",
        },
        {
            "model": "LSTM-combined",
            "test_n": 6000,
            "correct": 5730,
            "accuracy": 0.9550,
            "macro_precision": 0.9550,
            "macro_recall": 0.9550,
            "macro_f1": 0.9550,
            "approx_errors": 270,
            "note": "Two-branch sequence plus GPSD model.",
        },
        {
            "model": "BiLSTM-MHA",
            "test_n": 6000,
            "correct": 5820,
            "accuracy": 0.9700,
            "macro_precision": 0.9700,
            "macro_recall": 0.9700,
            "macro_f1": 0.9700,
            "approx_errors": 180,
            "note": "Approximate values from retained rounded accuracy.",
        },
    ]
    internal_rows: list[dict[str, str]] = []
    for spec in internal_specs:
        low, high = wilson_ci(spec["correct"], spec["test_n"])
        internal_rows.append(
            {
                "model": spec["model"],
                "test_n": str(spec["test_n"]),
                "accuracy": fmt(spec["accuracy"]),
                "accuracy_ci_low": fmt(low),
                "accuracy_ci_high": fmt(high),
                "macro_precision": fmt(spec["macro_precision"]),
                "macro_recall": fmt(spec["macro_recall"]),
                "macro_f1": fmt(spec["macro_f1"]),
                "approx_errors": str(spec["approx_errors"]),
                "note": spec["note"],
            }
        )
    fields_internal = [
        "model",
        "test_n",
        "accuracy",
        "accuracy_ci_low",
        "accuracy_ci_high",
        "macro_precision",
        "macro_recall",
        "macro_f1",
        "approx_errors",
        "note",
    ]
    write_csv(RESULTS_DIR / "table4_internal_model_comparison.csv", internal_rows, fields_internal)

    external_specs = [
        ("AMPDiscover", 1000, 0.9202, 439, 74, 61, 426),
        ("DDBL", 1000, 0.9986, 494, 10, 6, 490),
        ("EMBL", 1000, 0.9950, 482, 11, 18, 489),
        ("RefSeq", 1000, 0.9928, 478, 8, 22, 492),
        ("SSFGM", 1000, 0.8573, 383, 70, 117, 430),
        ("XU", 1536, 0.6605, 345, 159, 423, 609),
    ]
    external_rows: list[dict[str, str]] = []
    for dataset, test_n, auc, tp, fp, fn, tn in external_specs:
        correct = tp + tn
        accuracy = correct / test_n
        acc_low, acc_high = wilson_ci(correct, test_n)
        auc_low, auc_high = hanley_mcneil_auc_ci(auc, tp + fn, tn + fp)
        external_rows.append(
            {
                "dataset": dataset,
                "test_n": str(test_n),
                "accuracy": fmt(accuracy),
                "accuracy_ci_low": fmt(acc_low),
                "accuracy_ci_high": fmt(acc_high),
                "auc_roc": fmt(auc),
                "auc_ci_low": fmt(auc_low),
                "auc_ci_high": fmt(auc_high),
                "tp": str(tp),
                "fp": str(fp),
                "fn": str(fn),
                "tn": str(tn),
            }
        )
    fields_external = [
        "dataset",
        "test_n",
        "accuracy",
        "accuracy_ci_low",
        "accuracy_ci_high",
        "auc_roc",
        "auc_ci_low",
        "auc_ci_high",
        "tp",
        "fp",
        "fn",
        "tn",
    ]
    write_csv(RESULTS_DIR / "table6_lstm_external_validation.csv", external_rows, fields_external)

    cm_fields = ["true_label", "pred_nAMP", "pred_AMP"]
    write_csv(
        RESULTS_DIR / "svm_confusion_matrix.csv",
        [{"true_label": "nAMP", "pred_nAMP": "2940", "pred_AMP": "60"}, {"true_label": "AMP", "pred_nAMP": "120", "pred_AMP": "2880"}],
        cm_fields,
    )
    write_csv(
        RESULTS_DIR / "lstm_confusion_matrix.csv",
        [{"true_label": "nAMP", "pred_nAMP": "2880", "pred_AMP": "120"}, {"true_label": "AMP", "pred_nAMP": "150", "pred_AMP": "2850"}],
        cm_fields,
    )

    create_if_missing(
        FIGURES_DIR / "Fig1_controlled_pipeline.pdf",
        flow_pdf,
        "Controlled AMP Prediction Pipeline",
        [["Curated sequence pools", "Negative screening", "Redundancy reduction", "Fixed manifests"], ["GPSD descriptors", "Sequence encoding", "Held-out evaluation", "Leakage audit"]],
    )
    create_if_missing(
        FIGURES_DIR / "Fig2_svm_combined_architecture.pdf",
        flow_pdf,
        "SVM-Combined Architecture",
        [["Amino-acid sequence", "Fixed-length index encoding", "126 GPSD descriptors", "Feature scaling", "RBF-kernel SVM"]],
    )
    create_if_missing(
        FIGURES_DIR / "Fig3_recurrent_architectures.pdf",
        flow_pdf,
        "Recurrent Architectures",
        [["Sequence input", "Embedding", "LSTM branch", "Concatenate GPSD", "Dense classifier"], ["Sequence input", "Embedding", "BiLSTM", "Multi-head attention", "Dense classifier"]],
    )

    create_if_missing(FIGURES_DIR / "Fig4_svm_confusion_matrix.png", save_confusion_matrix, "SVM-combined confusion matrix", [[2940, 60], [120, 2880]])
    create_if_missing(FIGURES_DIR / "Fig5_internal_accuracy_CI.png", save_ci_plot, "Internal held-out accuracy with Wilson 95% CI", internal_rows, 0.94, 0.98)
    create_if_missing(FIGURES_DIR / "Fig6_external_accuracy_CI.png", save_ci_plot, "External LSTM-combined accuracy with Wilson 95% CI", external_rows, 0.55, 1.00)
    create_if_missing(FIGURES_DIR / "Fig7_lstm_confusion_matrix.png", save_confusion_matrix, "LSTM-combined confusion matrix", [[2880, 120], [150, 2850]])
    print(f"Wrote tables to {RESULTS_DIR}")
    print(f"Wrote figures to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
