import csv
import math
from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

MODEL_ORDER = ["SmolVLM", "Qwen-3B", "Qwen-7B"]
CONDITION_ORDER = ["implicit", "explicit"]
RISK_ORDER = ["low", "medium", "high"]

CONDITION_COLORS = {
    "implicit": "#2F80ED",
    "explicit": "#F2994A",
}

MODEL_COLORS = {
    "SmolVLM": "#BB6BD9",
    "Qwen-3B": "#27AE60",
    "Qwen-7B": "#EB5757",
}

METRICS = [
    ("mirage", "MIRAGE rate"),
    ("recognition", "Recognition rate"),
    ("explicit_abstention", "Explicit abstention rate"),
    ("hedged_answer", "Hedged answer rate"),
    ("confident_answer", "Confident answer rate"),
    ("hard_mirage", "Hard MIRAGE rate"),
    ("soft_mirage", "Soft MIRAGE rate"),
]

HEADLINE_METRICS = [
    ("mirage", "MIRAGE"),
    ("recognition", "Recognition"),
    ("explicit_abstention", "Abstain"),
    ("hard_mirage", "Hard MIRAGE"),
    ("soft_mirage", "Soft MIRAGE"),
]


def model_label(model_name):
    name = model_name or ""
    if "SmolVLM" in name:
        return "SmolVLM"
    if "7B" in name:
        return "Qwen-7B"
    if "3B" in name or "Qwen" in name:
        return "Qwen-3B"
    return name


def condition_label(condition):
    if condition == "implicit_no_image":
        return "implicit"
    if condition == "explicit_missing_image":
        return "explicit"
    return condition


def valid_row(row):
    return (
        row.get("run_status") == "success"
        and row.get("judge_parse_success") == "yes"
        and row.get("response_mode") != "unscorable"
    )


def read_scored(path="annotations/phantom0_all_scored.csv"):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    for r in rows:
        r["model_label"] = r.get("model_label") or model_label(r.get("model_name", ""))
        r["condition_clean"] = condition_label(r.get("condition", ""))
    return rows


def summarize(rows, group_cols):
    groups = defaultdict(list)
    for r in rows:
        key = tuple(r.get(c, "") for c in group_cols)
        groups[key].append(r)

    out = []
    for key, group in sorted(groups.items()):
        valid = [r for r in group if valid_row(r)]
        row = {c: key[i] for i, c in enumerate(group_cols)}
        row["n_attempted"] = len(group)
        row["n_valid"] = len(valid)
        row["n_unscorable"] = sum(1 for r in group if r.get("response_mode") == "unscorable")
        row["n_judge_parse_fail"] = sum(1 for r in group if r.get("judge_parse_success") != "yes")

        for metric, _ in METRICS:
            count = sum(1 for r in valid if r.get(metric) == "yes")
            row[f"{metric}_count"] = count
            row[f"{metric}_rate"] = count / len(valid) if valid else np.nan

        out.append(row)

    return out


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        return

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {path} rows={len(rows)}")


def sort_rows(rows, cols):
    def key(r):
        vals = []
        for c in cols:
            v = r.get(c, "")
            if c == "model_label":
                vals.append(MODEL_ORDER.index(v) if v in MODEL_ORDER else 99)
            elif c in {"condition", "condition_clean"}:
                vals.append(CONDITION_ORDER.index(v) if v in CONDITION_ORDER else 99)
            elif c == "risk_level":
                vals.append(RISK_ORDER.index(v) if v in RISK_ORDER else 99)
            else:
                vals.append(v)
        return vals

    return sorted(rows, key=key)


def pct_labels(ax, bars, values):
    for bar, val in zip(bars, values):
        if math.isnan(val):
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.015,
            f"{val * 100:.0f}%",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def save_grouped_condition_bars(rows, x_col, metric, title, outfile, x_order=None, xlabel=None):
    x_vals = x_order or sorted(set(r[x_col] for r in rows))
    x = np.arange(len(x_vals))
    width = 0.36

    plt.figure(figsize=(max(8, len(x_vals) * 0.9), 5))
    ax = plt.gca()

    for idx, cond in enumerate(CONDITION_ORDER):
        vals = []
        for xv in x_vals:
            match = next((r for r in rows if r[x_col] == xv and r["condition_clean"] == cond), None)
            vals.append(float(match.get(f"{metric}_rate", np.nan)) if match else np.nan)

        positions = x + (idx - 0.5) * width
        bars = ax.bar(positions, vals, width, label=cond, color=CONDITION_COLORS[cond], alpha=0.9)
        pct_labels(ax, bars, vals)

    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_ylabel("Rate")
    ax.set_xlabel(xlabel or x_col)
    ax.set_xticks(x)
    ax.set_xticklabels(x_vals, rotation=25, ha="right")
    ax.set_ylim(0, 1.08)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="Condition")
    plt.tight_layout()
    plt.savefig(outfile, dpi=220)
    plt.close()
    print(f"wrote {outfile}")


def save_primary_bars(primary):
    for metric, label in METRICS:
        save_grouped_condition_bars(
            primary,
            x_col="model_label",
            metric=metric,
            title=f"{label} by model and prompt condition",
            outfile=f"figures/comprehensive/primary_{metric}_by_model_condition.png",
            x_order=MODEL_ORDER,
            xlabel="Model",
        )


def save_prompt_slope(primary):
    for metric, label in HEADLINE_METRICS:
        plt.figure(figsize=(7, 5))
        ax = plt.gca()

        for model in MODEL_ORDER:
            vals = []
            for cond in CONDITION_ORDER:
                match = next((r for r in primary if r["model_label"] == model and r["condition_clean"] == cond), None)
                vals.append(float(match.get(f"{metric}_rate", np.nan)) if match else np.nan)

            ax.plot([0, 1], vals, marker="o", linewidth=2.5, label=model, color=MODEL_COLORS[model])

            if not any(math.isnan(v) for v in vals):
                ax.text(-0.03, vals[0], f"{vals[0] * 100:.1f}%", ha="right", va="center", fontsize=8)
                ax.text(1.03, vals[1], f"{vals[1] * 100:.1f}%", ha="left", va="center", fontsize=8)

        ax.set_title(f"Prompt effect on {label}", fontsize=14, weight="bold")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["implicit", "explicit"])
        ax.set_ylabel("Rate")
        ax.set_ylim(0, 1.05)
        ax.grid(axis="y", alpha=0.25)
        ax.legend(title="Model", loc="best")
        plt.tight_layout()

        outfile = f"figures/comprehensive/prompt_effect_{metric}_slope.png"
        plt.savefig(outfile, dpi=220)
        plt.close()
        print(f"wrote {outfile}")


def save_overview_heatmap(primary):
    matrix = []
    row_labels = []

    for model in MODEL_ORDER:
        for cond in CONDITION_ORDER:
            row = next((r for r in primary if r["model_label"] == model and r["condition_clean"] == cond), None)
            row_labels.append(f"{model} / {cond}")
            matrix.append([float(row.get(f"{m}_rate", np.nan)) if row else np.nan for m, _ in HEADLINE_METRICS])

    col_labels = [label for _, label in HEADLINE_METRICS]
    data = np.array(matrix, dtype=float)

    plt.figure(figsize=(9, 5.5))
    ax = plt.gca()
    im = ax.imshow(data, vmin=0, vmax=1, cmap="viridis")

    ax.set_title("Headline Phantom-0 rates by model and condition", fontsize=14, weight="bold")
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_xticklabels(col_labels, rotation=30, ha="right")
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not math.isnan(data[i, j]):
                ax.text(
                    j,
                    i,
                    f"{data[i, j] * 100:.0f}%",
                    ha="center",
                    va="center",
                    color="white" if data[i, j] > 0.5 else "black",
                    fontsize=8,
                )

    cbar = plt.colorbar(im)
    cbar.set_label("Rate")
    plt.tight_layout()

    outfile = "figures/comprehensive/headline_rates_heatmap.png"
    plt.savefig(outfile, dpi=220)
    plt.close()
    print(f"wrote {outfile}")


def save_risk_bars(by_risk_condition):
    wanted = [
        ("mirage", "MIRAGE rate"),
        ("recognition", "Recognition rate"),
        ("hard_mirage", "Hard MIRAGE rate"),
        ("explicit_abstention", "Explicit abstention rate"),
    ]

    for metric, label in wanted:
        x_labels = []
        for model in MODEL_ORDER:
            for risk in RISK_ORDER:
                x_labels.append(f"{model}\n{risk}")

        plt.figure(figsize=(11, 5.5))
        ax = plt.gca()
        x = np.arange(len(x_labels))
        width = 0.36

        for idx, cond in enumerate(CONDITION_ORDER):
            vals = []
            for label_text in x_labels:
                model, risk = label_text.split("\n")
                match = next(
                    (
                        r
                        for r in by_risk_condition
                        if r["model_label"] == model
                        and r["risk_level"] == risk
                        and r["condition_clean"] == cond
                    ),
                    None,
                )
                vals.append(float(match.get(f"{metric}_rate", np.nan)) if match else np.nan)

            positions = x + (idx - 0.5) * width
            ax.bar(positions, vals, width, label=cond, color=CONDITION_COLORS[cond], alpha=0.9)

        for boundary in [2.5, 5.5]:
            ax.axvline(boundary, color="black", alpha=0.15, linewidth=1)

        ax.set_title(f"{label} by risk level, ordered by model", fontsize=14, weight="bold")
        ax.set_ylabel("Rate")
        ax.set_ylim(0, 1.05)
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=0, fontsize=8)
        ax.grid(axis="y", alpha=0.25)
        ax.legend(title="Condition")
        plt.tight_layout()

        outfile = f"figures/comprehensive/risk_{metric}_by_model_condition.png"
        plt.savefig(outfile, dpi=220)
        plt.close()
        print(f"wrote {outfile}")


def pivot_matrix(rows, row_col, metric):
    row_values = sorted(set(r[row_col] for r in rows))
    col_keys = [(m, c) for m in MODEL_ORDER for c in CONDITION_ORDER]

    matrix = []
    for rv in row_values:
        line = []
        for model, cond in col_keys:
            match = next(
                (
                    r
                    for r in rows
                    if r[row_col] == rv
                    and r["model_label"] == model
                    and r["condition_clean"] == cond
                ),
                None,
            )
            line.append(float(match.get(f"{metric}_rate", np.nan)) if match else np.nan)
        matrix.append(line)

    col_labels = [f"{m}\n{c}" for m, c in col_keys]
    return row_values, col_labels, np.array(matrix, dtype=float)


def save_heatmap(rows, row_col, metric, title, outfile):
    row_values, col_labels, data = pivot_matrix(rows, row_col, metric)
    height = max(5, len(row_values) * 0.34)

    plt.figure(figsize=(9, height))
    ax = plt.gca()

    cmap = plt.cm.magma.copy()
    cmap.set_bad(color="#f2f2f2")

    im = ax.imshow(data, vmin=0, vmax=1, cmap=cmap, aspect="auto")

    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=8)
    ax.set_yticks(np.arange(len(row_values)))
    ax.set_yticklabels(row_values, fontsize=8)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not math.isnan(data[i, j]):
                ax.text(
                    j,
                    i,
                    f"{data[i, j] * 100:.0f}",
                    ha="center",
                    va="center",
                    color="white" if data[i, j] > 0.45 else "black",
                    fontsize=7,
                )

    cbar = plt.colorbar(im)
    cbar.set_label("Rate")
    plt.tight_layout()
    plt.savefig(outfile, dpi=220)
    plt.close()
    print(f"wrote {outfile}")


def save_qwen_dumbbells(primary):
    for cond in CONDITION_ORDER:
        labels = [label for _, label in HEADLINE_METRICS]
        q3 = []
        q7 = []

        for metric, _ in HEADLINE_METRICS:
            row3 = next((r for r in primary if r["model_label"] == "Qwen-3B" and r["condition_clean"] == cond), None)
            row7 = next((r for r in primary if r["model_label"] == "Qwen-7B" and r["condition_clean"] == cond), None)
            q3.append(float(row3.get(f"{metric}_rate", np.nan)) if row3 else np.nan)
            q7.append(float(row7.get(f"{metric}_rate", np.nan)) if row7 else np.nan)

        y = np.arange(len(labels))

        plt.figure(figsize=(8, 5))
        ax = plt.gca()

        for i in range(len(labels)):
            ax.plot([q3[i], q7[i]], [y[i], y[i]], color="#999999", linewidth=2, alpha=0.8)

        ax.scatter(q3, y, label="Qwen-3B", color=MODEL_COLORS["Qwen-3B"], s=70)
        ax.scatter(q7, y, label="Qwen-7B", color=MODEL_COLORS["Qwen-7B"], s=70)

        ax.set_title(f"Qwen family comparison ({cond})", fontsize=14, weight="bold")
        ax.set_xlabel("Rate")
        ax.set_xlim(0, 1)
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.grid(axis="x", alpha=0.25)
        ax.legend()
        plt.tight_layout()

        outfile = f"figures/comprehensive/qwen_family_{cond}_dumbbell.png"
        plt.savefig(outfile, dpi=220)
        plt.close()
        print(f"wrote {outfile}")


def save_judge_agreement(path="metrics/phantom0_judge_agreement.csv"):
    p = Path(path)
    if not p.exists():
        print("judge agreement file not found; skipping")
        return

    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))

    labels = [r["field"].replace("_", "\n") for r in rows]
    agreement = [float(r["percent_agreement"]) for r in rows]
    kappa = [float(r["cohens_kappa"]) for r in rows]

    x = np.arange(len(labels))
    width = 0.36

    plt.figure(figsize=(8, 5))
    ax = plt.gca()

    ax.bar(x - width / 2, agreement, width, label="Percent agreement", color="#56CCF2")
    ax.bar(x + width / 2, kappa, width, label="Cohen's κ", color="#9B51E0")

    ax.set_title("Automatic judge vs human audit agreement", fontsize=14, weight="bold")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    plt.tight_layout()

    outfile = "figures/comprehensive/judge_agreement.png"
    plt.savefig(outfile, dpi=220)
    plt.close()
    print(f"wrote {outfile}")


def write_figure_index():
    files = sorted(Path("figures/comprehensive").glob("*.png"))

    lines = ["# Comprehensive Phantom-0 Figure Index\n"]
    lines.append("These figures extend the Week 5 visual analysis. Most figures show both implicit and explicit conditions where possible.\n")

    for f in files:
        lines.append(f"- `{f.as_posix()}`")

    Path("reports").mkdir(exist_ok=True)
    Path("reports/phantom0_comprehensive_figure_index.md").write_text("\n".join(lines), encoding="utf-8")

    print("wrote reports/phantom0_comprehensive_figure_index.md")


def main():
    Path("figures/comprehensive").mkdir(parents=True, exist_ok=True)

    rows = read_scored()

    primary = summarize(rows, ["model_label", "condition_clean"])
    primary = sort_rows(primary, ["model_label", "condition_clean"])

    by_risk_condition = summarize(rows, ["model_label", "condition_clean", "risk_level"])
    by_risk_condition = sort_rows(by_risk_condition, ["model_label", "risk_level", "condition_clean"])

    by_question_condition = summarize(rows, ["model_label", "condition_clean", "question_type"])
    by_question_condition = sort_rows(by_question_condition, ["question_type", "model_label", "condition_clean"])

    by_domain_category_condition = summarize(rows, ["model_label", "condition_clean", "domain", "category"])
    by_domain_category_condition = sort_rows(by_domain_category_condition, ["domain", "category", "model_label", "condition_clean"])

    write_csv("metrics/phantom0_by_risk_condition.csv", by_risk_condition)
    write_csv("metrics/phantom0_by_question_type_condition.csv", by_question_condition)
    write_csv("metrics/phantom0_by_domain_category_condition.csv", by_domain_category_condition)

    save_primary_bars(primary)
    save_overview_heatmap(primary)
    save_prompt_slope(primary)
    save_risk_bars(by_risk_condition)

    for metric, label in [
        ("mirage", "MIRAGE rate"),
        ("recognition", "Recognition rate"),
        ("hard_mirage", "Hard MIRAGE rate"),
        ("explicit_abstention", "Explicit abstention rate"),
    ]:
        save_heatmap(
            by_question_condition,
            "question_type",
            metric,
            f"{label} by question type, model, and condition",
            f"figures/comprehensive/question_type_{metric}_heatmap.png",
        )

    for metric, label in [
        ("mirage", "MIRAGE rate"),
        ("recognition", "Recognition rate"),
        ("hard_mirage", "Hard MIRAGE rate"),
        ("explicit_abstention", "Explicit abstention rate"),
    ]:
        save_heatmap(
            by_domain_category_condition,
            "category",
            metric,
            f"{label} by domain/category, model, and condition",
            f"figures/comprehensive/domain_category_{metric}_heatmap.png",
        )

    save_qwen_dumbbells(primary)
    save_judge_agreement()
    write_figure_index()

    print("\nDone. Check figures/comprehensive/ and reports/phantom0_comprehensive_figure_index.md")


if __name__ == "__main__":
    main()
