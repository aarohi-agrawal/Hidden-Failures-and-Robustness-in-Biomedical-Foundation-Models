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
    "SmolVLM": "#9B51E0",
    "Qwen-3B": "#27AE60",
    "Qwen-7B": "#EB5757",
}

FAILURE_METRICS = [
    ("mirage", "MIRAGE"),
    ("hard_mirage", "Hard MIRAGE"),
    ("soft_mirage", "Soft MIRAGE"),
    ("confident_answer", "Confident Answer"),
]

SAFETY_METRICS = [
    ("recognition", "Recognition"),
    ("explicit_abstention", "Explicit Abstention"),
]

ANSWER_MODE_METRICS = [
    ("confident_answer", "Confident Answer"),
    ("hedged_answer", "Hedged Answer"),
    ("explicit_abstention", "Explicit Abstention"),
]

ALL_METRICS = [
    ("mirage", "MIRAGE"),
    ("recognition", "Recognition"),
    ("explicit_abstention", "Explicit Abstention"),
    ("hedged_answer", "Hedged Answer"),
    ("confident_answer", "Confident Answer"),
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
        r["model_label"] = model_label(r.get("model_name", ""))
        r["condition_clean"] = condition_label(r.get("condition", ""))
    return rows


def summarize(rows, group_cols):
    groups = defaultdict(list)
    for r in rows:
        key = tuple(r.get(c, "") for c in group_cols)
        groups[key].append(r)

    out = []
    for key, group in groups.items():
        valid = [r for r in group if valid_row(r)]

        row = {c: key[i] for i, c in enumerate(group_cols)}
        row["n_attempted"] = len(group)
        row["n_valid"] = len(valid)
        row["n_judge_parse_fail"] = sum(1 for r in group if r.get("judge_parse_success") != "yes")
        row["n_unscorable"] = sum(1 for r in group if r.get("response_mode") == "unscorable")

        for metric, _ in ALL_METRICS:
            count = sum(1 for r in valid if r.get(metric) == "yes")
            row[f"{metric}_count"] = count
            row[f"{metric}_rate"] = count / len(valid) if valid else np.nan

        out.append(row)

    return out


def sort_rows(rows, cols):
    def key(row):
        values = []
        for c in cols:
            v = row.get(c, "")
            if c == "model_label":
                values.append(MODEL_ORDER.index(v) if v in MODEL_ORDER else 99)
            elif c == "condition_clean":
                values.append(CONDITION_ORDER.index(v) if v in CONDITION_ORDER else 99)
            elif c == "risk_level":
                values.append(RISK_ORDER.index(v) if v in RISK_ORDER else 99)
            else:
                values.append(v)
        return values
    return sorted(rows, key=key)


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


def pct(value):
    if value is None or value == "" or math.isnan(float(value)):
        return ""
    return f"{float(value) * 100:.0f}%"


def get_rate(rows, filters, metric):
    for r in rows:
        if all(r.get(k) == v for k, v in filters.items()):
            return float(r.get(f"{metric}_rate", np.nan))
    return np.nan


def clean_old_figures():
    fig_dir = Path("figures/comprehensive")
    fig_dir.mkdir(parents=True, exist_ok=True)
    for p in fig_dir.glob("*.png"):
        p.unlink()


def add_bar_labels(ax, bars, vals):
    for bar, val in zip(bars, vals):
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


def grouped_condition_bar(rows, x_values, x_filter_name, metric, title, outfile, xlabel):
    x = np.arange(len(x_values))
    width = 0.36

    fig, ax = plt.subplots(figsize=(max(8, len(x_values) * 0.9), 5))

    for i, cond in enumerate(CONDITION_ORDER):
        vals = [
            get_rate(rows, {x_filter_name: xval, "condition_clean": cond}, metric)
            for xval in x_values
        ]

        bars = ax.bar(
            x + (i - 0.5) * width,
            vals,
            width,
            label=cond,
            color=CONDITION_COLORS[cond],
            alpha=0.9,
        )
        add_bar_labels(ax, bars, vals)

    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Rate")
    ax.set_ylim(0, 1.08)
    ax.set_xticks(x)
    ax.set_xticklabels(x_values, rotation=25, ha="right")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="Condition")
    fig.tight_layout()
    fig.savefig(outfile, dpi=220)
    plt.close(fig)
    print(f"wrote {outfile}")


def heatmap(data, row_labels, col_labels, title, outfile, cmap_name, note=None):
    data = np.array(data, dtype=float)

    height = max(4.5, len(row_labels) * 0.4)
    width = max(7.5, len(col_labels) * 1.1)

    fig, ax = plt.subplots(figsize=(width, height))
    cmap = plt.cm.get_cmap(cmap_name).copy()
    cmap.set_bad(color="#F2F2F2")

    im = ax.imshow(data, vmin=0, vmax=1, cmap=cmap, aspect="auto")

    ax.set_title(title, fontsize=14, weight="bold", pad=15)
    if note:
        ax.text(0, -0.12, note, transform=ax.transAxes, fontsize=9, alpha=0.8)

    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_xticklabels(col_labels, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=8)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not math.isnan(data[i, j]):
                ax.text(
                    j,
                    i,
                    f"{data[i, j] * 100:.0f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="white" if data[i, j] > 0.45 else "black",
                )

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Rate")
    fig.tight_layout()
    fig.savefig(outfile, dpi=220)
    plt.close(fig)
    print(f"wrote {outfile}")


def headline_heatmaps(primary):
    row_labels = []
    for model in MODEL_ORDER:
        for cond in CONDITION_ORDER:
            row_labels.append(f"{model} / {cond}")

    def build(metric_list):
        matrix = []
        for model in MODEL_ORDER:
            for cond in CONDITION_ORDER:
                matrix.append([
                    get_rate(primary, {"model_label": model, "condition_clean": cond}, metric)
                    for metric, _ in metric_list
                ])
        return matrix, [label for _, label in metric_list]

    failure_data, failure_cols = build(FAILURE_METRICS)
    heatmap(
        failure_data,
        row_labels,
        failure_cols,
        "Failure metrics: higher is worse",
        "figures/comprehensive/headline_failure_rates_heatmap.png",
        "magma",
        note="Groups MIRAGE-style failure behavior together so the direction is consistent.",
    )

    safety_data, safety_cols = build(SAFETY_METRICS)
    heatmap(
        safety_data,
        row_labels,
        safety_cols,
        "Safety metrics: higher is better",
        "figures/comprehensive/headline_safety_rates_heatmap.png",
        "viridis",
        note="Recognition and explicit abstention are grouped because both reflect safer missing-evidence behavior.",
    )

    mode_data, mode_cols = build(ANSWER_MODE_METRICS)
    heatmap(
        mode_data,
        row_labels,
        mode_cols,
        "Answer mode distribution",
        "figures/comprehensive/headline_answer_mode_heatmap.png",
        "cividis",
        note="Shows whether models answer confidently, hedge, or explicitly abstain.",
    )


def primary_bars(primary):
    for metric, label in ALL_METRICS:
        grouped_condition_bar(
            primary,
            MODEL_ORDER,
            "model_label",
            metric,
            f"{label} by model and condition",
            f"figures/comprehensive/primary_{metric}_by_model_condition.png",
            "Model",
        )


def prompt_effect_slopes(primary):
    groups = [
        ("failure", FAILURE_METRICS, "Prompt effect on failure metrics", "figures/comprehensive/prompt_effect_failure_metrics.png"),
        ("safety", SAFETY_METRICS, "Prompt effect on safety metrics", "figures/comprehensive/prompt_effect_safety_metrics.png"),
    ]

    for _, metrics, title, outfile in groups:
        n = len(metrics)
        fig, axes = plt.subplots(1, n, figsize=(max(8, n * 4), 4.8), sharey=True)
        if n == 1:
            axes = [axes]

        for ax, (metric, label) in zip(axes, metrics):
            for model in MODEL_ORDER:
                vals = [
                    get_rate(primary, {"model_label": model, "condition_clean": cond}, metric)
                    for cond in CONDITION_ORDER
                ]
                ax.plot([0, 1], vals, marker="o", linewidth=2.5, color=MODEL_COLORS[model], label=model)
                if not any(math.isnan(v) for v in vals):
                    ax.text(-0.04, vals[0], f"{vals[0]*100:.1f}%", ha="right", va="center", fontsize=8)
                    ax.text(1.04, vals[1], f"{vals[1]*100:.1f}%", ha="left", va="center", fontsize=8)

            ax.set_title(label, fontsize=12, weight="bold")
            ax.set_xticks([0, 1])
            ax.set_xticklabels(["implicit", "explicit"])
            ax.set_ylim(0, 1.05)
            ax.grid(axis="y", alpha=0.25)

        axes[0].set_ylabel("Rate")
        axes[-1].legend(title="Model", loc="best")
        fig.suptitle(title, fontsize=15, weight="bold")
        fig.tight_layout()
        fig.savefig(outfile, dpi=220)
        plt.close(fig)
        print(f"wrote {outfile}")


def risk_figures(by_risk):
    wanted = [
        ("mirage", "MIRAGE rate"),
        ("hard_mirage", "Hard MIRAGE rate"),
        ("recognition", "Recognition rate"),
        ("explicit_abstention", "Explicit abstention rate"),
    ]

    for metric, label in wanted:
        x_labels = []
        for model in MODEL_ORDER:
            for risk in RISK_ORDER:
                x_labels.append(f"{model}\n{risk}")

        x = np.arange(len(x_labels))
        width = 0.36

        fig, ax = plt.subplots(figsize=(11, 5.5))

        for i, cond in enumerate(CONDITION_ORDER):
            vals = []
            for lab in x_labels:
                model, risk = lab.split("\n")
                vals.append(get_rate(by_risk, {"model_label": model, "risk_level": risk, "condition_clean": cond}, metric))

            ax.bar(
                x + (i - 0.5) * width,
                vals,
                width,
                label=cond,
                color=CONDITION_COLORS[cond],
                alpha=0.9,
            )

        for boundary in [2.5, 5.5]:
            ax.axvline(boundary, color="black", alpha=0.15)

        ax.set_title(f"{label} by risk level, ordered by model", fontsize=14, weight="bold")
        ax.set_ylabel("Rate")
        ax.set_ylim(0, 1.05)
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, fontsize=8)
        ax.grid(axis="y", alpha=0.25)
        ax.legend(title="Condition")
        fig.tight_layout()

        outfile = f"figures/comprehensive/risk_{metric}_by_model_condition.png"
        fig.savefig(outfile, dpi=220)
        plt.close(fig)
        print(f"wrote {outfile}")


def order_categories(rows, row_col, metric):
    scores = defaultdict(list)
    for r in rows:
        val = r.get(f"{metric}_rate")
        try:
            scores[r[row_col]].append(float(val))
        except Exception:
            pass

    ranked = []
    for key, vals in scores.items():
        vals = [v for v in vals if not math.isnan(v)]
        if vals:
            ranked.append((sum(vals) / len(vals), key))

    return [key for _, key in sorted(ranked, reverse=True)]


def condition_heatmap(rows, row_col, metric, title, outfile, top_n=None):
    row_values = order_categories(rows, row_col, metric)
    if top_n:
        row_values = row_values[:top_n]

    col_keys = [(m, c) for m in MODEL_ORDER for c in CONDITION_ORDER]
    col_labels = [f"{m}\n{c}" for m, c in col_keys]

    matrix = []
    for rv in row_values:
        matrix.append([
            get_rate(rows, {"model_label": m, "condition_clean": c, row_col: rv}, metric)
            for m, c in col_keys
        ])

    heatmap(
        matrix,
        row_values,
        col_labels,
        title,
        outfile,
        "magma" if metric in {"mirage", "hard_mirage", "soft_mirage", "confident_answer"} else "viridis",
        note="Rows are sorted by average rate. Smaller subgroup Ns should be interpreted as exploratory.",
    )


def question_and_domain_heatmaps(by_question, by_domain):
    for metric, label in [
        ("mirage", "MIRAGE rate"),
        ("hard_mirage", "Hard MIRAGE rate"),
        ("recognition", "Recognition rate"),
        ("explicit_abstention", "Explicit abstention rate"),
    ]:
        condition_heatmap(
            by_question,
            "question_type",
            metric,
            f"{label} by question type, model, and condition",
            f"figures/comprehensive/question_type_{metric}_heatmap.png",
        )

    for metric, label in [
        ("mirage", "MIRAGE rate"),
        ("hard_mirage", "Hard MIRAGE rate"),
        ("recognition", "Recognition rate"),
        ("explicit_abstention", "Explicit abstention rate"),
    ]:
        condition_heatmap(
            by_domain,
            "category",
            metric,
            f"{label} by domain/category, model, and condition",
            f"figures/comprehensive/domain_category_{metric}_heatmap.png",
        )
        condition_heatmap(
            by_domain,
            "category",
            metric,
            f"Top domain/category {label} pockets",
            f"figures/comprehensive/domain_category_top15_{metric}_heatmap.png",
            top_n=15,
        )


def qwen_dumbbells(primary):
    groups = [
        ("failure", FAILURE_METRICS, "Qwen family failure metrics"),
        ("safety", SAFETY_METRICS, "Qwen family safety metrics"),
    ]

    for cond in CONDITION_ORDER:
        for group_name, metric_list, title in groups:
            labels = [label for _, label in metric_list]
            q3 = [get_rate(primary, {"model_label": "Qwen-3B", "condition_clean": cond}, m) for m, _ in metric_list]
            q7 = [get_rate(primary, {"model_label": "Qwen-7B", "condition_clean": cond}, m) for m, _ in metric_list]

            y = np.arange(len(labels))

            fig, ax = plt.subplots(figsize=(8, max(4, len(labels) * 0.7)))
            for i in range(len(labels)):
                ax.plot([q3[i], q7[i]], [y[i], y[i]], color="#AAAAAA", linewidth=2, alpha=0.9)

            ax.scatter(q3, y, s=80, label="Qwen-3B", color=MODEL_COLORS["Qwen-3B"])
            ax.scatter(q7, y, s=80, label="Qwen-7B", color=MODEL_COLORS["Qwen-7B"])

            for i in range(len(labels)):
                if not math.isnan(q3[i]):
                    ax.text(q3[i], y[i] + 0.12, f"{q3[i]*100:.1f}%", ha="center", fontsize=8)
                if not math.isnan(q7[i]):
                    ax.text(q7[i], y[i] - 0.18, f"{q7[i]*100:.1f}%", ha="center", fontsize=8)

            ax.set_title(f"{title} ({cond})", fontsize=14, weight="bold")
            ax.set_xlabel("Rate")
            ax.set_xlim(0, 1)
            ax.set_yticks(y)
            ax.set_yticklabels(labels)
            ax.grid(axis="x", alpha=0.25)
            ax.legend()
            fig.tight_layout()

            outfile = f"figures/comprehensive/qwen_family_{group_name}_{cond}_dumbbell.png"
            fig.savefig(outfile, dpi=220)
            plt.close(fig)
            print(f"wrote {outfile}")


def judge_agreement_figure(path="metrics/phantom0_judge_agreement.csv"):
    p = Path(path)
    if not p.exists():
        return

    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    labels = [r["field"].replace("_", "\n") for r in rows]
    agreement = [float(r["percent_agreement"]) for r in rows]
    kappa = [float(r["cohens_kappa"]) for r in rows]

    x = np.arange(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, agreement, width, label="Percent agreement", color="#56CCF2")
    ax.bar(x + width / 2, kappa, width, label="Cohen's κ", color="#9B51E0")

    ax.set_title("Automatic judge vs human audit agreement", fontsize=14, weight="bold")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()

    outfile = "figures/comprehensive/judge_agreement.png"
    fig.savefig(outfile, dpi=220)
    plt.close(fig)
    print(f"wrote {outfile}")


def esc(text):
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def short(text, n=190):
    text = esc(text)
    return text if len(text) <= n else text[: n - 3] + "..."


def representative_examples(rows):
    examples = []

    def add(name, predicate, takeaway):
        match = next((r for r in rows if predicate(r)), None)
        if match:
            examples.append({
                "example": name,
                "model": match["model_label"],
                "condition": match["condition_clean"],
                "question": short(match.get("question", "")),
                "response": short(match.get("raw_response", "")),
                "takeaway": takeaway,
            })

    add(
        "SmolVLM hard MIRAGE",
        lambda r: r["model_label"] == "SmolVLM" and r["condition_clean"] == "implicit" and r.get("hard_mirage") == "yes",
        "Unsupported specific visual claim under missing visual evidence.",
    )

    add(
        "Qwen implicit failure",
        lambda r: r["model_label"].startswith("Qwen") and r["condition_clean"] == "implicit" and r.get("mirage") == "yes",
        "Qwen is safer overall, but not failure-free.",
    )

    add(
        "Explicit safe abstention",
        lambda r: r["condition_clean"] == "explicit" and r.get("explicit_abstention") == "yes",
        "Explicit missing-image prompt can trigger safer refusal behavior.",
    )

    add(
        "Hedged answer",
        lambda r: r.get("response_mode") == "hedged_answer",
        "Model gives a candidate answer but expresses uncertainty.",
    )

    lines = ["# Phantom-0 Representative Examples\n"]
    lines.append("These examples connect the quantitative metrics back to actual model behavior.\n")
    lines.append("| Example | Model | Condition | Question | Raw response | Takeaway |")
    lines.append("|---|---|---|---|---|---|")

    for ex in examples:
        lines.append(
            f"| {ex['example']} | {ex['model']} | {ex['condition']} | {ex['question']} | {ex['response']} | {ex['takeaway']} |"
        )

    Path("reports/phantom0_representative_examples.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote reports/phantom0_representative_examples.md")


def figure_index():
    main = [
        ("headline_failure_rates_heatmap.png", "Groups failure metrics where higher is worse.", "Shows whether unsupported answering clusters by model/condition."),
        ("headline_safety_rates_heatmap.png", "Groups safety metrics where higher is better.", "Shows recognition and abstention together."),
        ("primary_mirage_by_model_condition.png", "Main MIRAGE comparison.", "Best single plot for the core result."),
        ("prompt_effect_failure_metrics.png", "Implicit vs explicit prompt effect for failure metrics.", "Shows whether explicit missing-image framing reduces failure."),
        ("prompt_effect_safety_metrics.png", "Implicit vs explicit prompt effect for safety metrics.", "Shows whether explicit framing increases recognition/abstention."),
        ("risk_mirage_by_model_condition.png", "Risk breakdown ordered by model.", "Addresses the requested model-first risk layout."),
        ("question_type_mirage_heatmap.png", "Question-type MIRAGE heatmap.", "Finds failure pockets by question type."),
        ("domain_category_top15_mirage_heatmap.png", "Top domain/category MIRAGE pockets.", "Finds concentrated weak spots without overwhelming the reader."),
        ("qwen_family_failure_implicit_dumbbell.png", "Qwen-3B vs Qwen-7B failure comparison.", "Shows within-family difference without claiming scale causality."),
        ("judge_agreement.png", "Human audit vs automatic judge.", "Validates which metrics are most reliable."),
    ]

    lines = ["# Comprehensive Phantom-0 Figure Index\n"]
    lines.append("Figures are divided into main figures and appendix/supporting figures. Most figures show both implicit and explicit conditions wherever possible.\n")

    lines.append("## Main figures\n")
    lines.append("| File | Purpose | Takeaway |")
    lines.append("|---|---|---|")
    for fname, purpose, takeaway in main:
        lines.append(f"| `figures/comprehensive/{fname}` | {purpose} | {takeaway} |")

    all_files = sorted(p.name for p in Path("figures/comprehensive").glob("*.png"))
    main_names = {m[0] for m in main}
    appendix = [f for f in all_files if f not in main_names]

    lines.append("\n## Appendix/supporting figures\n")
    for f in appendix:
        lines.append(f"- `figures/comprehensive/{f}`")

    Path("reports/phantom0_comprehensive_figure_index.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote reports/phantom0_comprehensive_figure_index.md")


def main():
    Path("metrics").mkdir(exist_ok=True)
    Path("figures/comprehensive").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(exist_ok=True)

    clean_old_figures()

    rows = read_scored()

    primary = sort_rows(summarize(rows, ["model_label", "condition_clean"]), ["model_label", "condition_clean"])
    by_risk = sort_rows(summarize(rows, ["model_label", "condition_clean", "risk_level"]), ["model_label", "risk_level", "condition_clean"])
    by_question = sort_rows(summarize(rows, ["model_label", "condition_clean", "question_type"]), ["question_type", "model_label", "condition_clean"])
    by_domain = sort_rows(summarize(rows, ["model_label", "condition_clean", "domain", "category"]), ["domain", "category", "model_label", "condition_clean"])

    write_csv("metrics/phantom0_by_risk_condition.csv", by_risk)
    write_csv("metrics/phantom0_by_question_type_condition.csv", by_question)
    write_csv("metrics/phantom0_by_domain_category_condition.csv", by_domain)

    primary_bars(primary)
    headline_heatmaps(primary)
    prompt_effect_slopes(primary)
    risk_figures(by_risk)
    question_and_domain_heatmaps(by_question, by_domain)
    qwen_dumbbells(primary)
    judge_agreement_figure()
    representative_examples(rows)
    figure_index()

    print("\nDone. Main review files:")
    print("- reports/phantom0_comprehensive_figure_index.md")
    print("- reports/phantom0_representative_examples.md")
    print("- figures/comprehensive/")


if __name__ == "__main__":
    main()
