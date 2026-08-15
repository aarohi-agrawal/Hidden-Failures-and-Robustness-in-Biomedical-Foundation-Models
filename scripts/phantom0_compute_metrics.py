import csv
import random
from pathlib import Path
from collections import defaultdict

METRICS = [
    "mirage",
    "recognition",
    "explicit_abstention",
    "hedged_answer",
    "confident_answer",
    "hard_mirage",
    "soft_mirage",
]

PRIMARY_GROUPS = ["model_label", "condition"]
RISK_GROUPS = ["model_label", "risk_level"]
QUESTION_GROUPS = ["model_label", "question_type"]
DOMAIN_CATEGORY_GROUPS = ["model_label", "domain", "category"]

RANDOM_SEED = 13
BOOTSTRAPS = 2000


def model_label(model_name):
    name = model_name or ""
    if "SmolVLM" in name:
        return "SmolVLM"
    if "7B" in name:
        return "Qwen-7B"
    if "3B" in name or "Qwen" in name:
        return "Qwen-3B"
    return name


def clean_condition(condition):
    if condition == "implicit_no_image":
        return "implicit"
    if condition == "explicit_missing_image":
        return "explicit"
    return condition


def is_valid(row):
    return (
        row.get("run_status") == "success"
        and row.get("judge_parse_success") == "yes"
        and row.get("response_mode") != "unscorable"
    )


def metric_rate(rows, metric):
    if not rows:
        return ""
    return sum(1 for r in rows if r.get(metric) == "yes") / len(rows)


def bootstrap_ci(rows, metric, n_boot=BOOTSTRAPS):
    if not rows:
        return "", ""

    by_source = defaultdict(list)
    for r in rows:
        by_source[r["source_id"]].append(r)

    source_ids = list(by_source.keys())
    if len(source_ids) < 2:
        rate = metric_rate(rows, metric)
        return rate, rate

    rng = random.Random(RANDOM_SEED)
    vals = []

    for _ in range(n_boot):
        sampled = []
        for sid in rng.choices(source_ids, k=len(source_ids)):
            sampled.extend(by_source[sid])
        vals.append(metric_rate(sampled, metric))

    vals.sort()
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(0.975 * (len(vals) - 1))]
    return lo, hi


def summarize_group(rows, group_cols):
    groups = defaultdict(list)
    for r in rows:
        key = tuple(r.get(c, "") for c in group_cols)
        groups[key].append(r)

    output = []
    for key, group in sorted(groups.items()):
        valid = [r for r in group if is_valid(r)]
        unscorable = [r for r in group if r.get("response_mode") == "unscorable"]
        judge_fail = [r for r in group if r.get("judge_parse_success") != "yes"]
        run_errors = [r for r in group if r.get("run_status") != "success" or r.get("error")]

        out = {c: key[i] for i, c in enumerate(group_cols)}
        out.update({
            "n_attempted": len(group),
            "n_valid": len(valid),
            "n_unscorable": len(unscorable),
            "n_judge_parse_fail": len(judge_fail),
            "n_run_error": len(run_errors),
        })

        for metric in METRICS:
            count = sum(1 for r in valid if r.get(metric) == "yes")
            rate = metric_rate(valid, metric)
            lo, hi = bootstrap_ci(valid, metric)

            out[f"{metric}_count"] = count
            out[f"{metric}_rate"] = "" if rate == "" else round(rate, 4)
            out[f"{metric}_ci_low"] = "" if lo == "" else round(lo, 4)
            out[f"{metric}_ci_high"] = "" if hi == "" else round(hi, 4)

        output.append(out)

    return output


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {path} rows={len(rows)}")


def read_rows(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    for r in rows:
        r["model_label"] = model_label(r.get("model_name", ""))
        r["condition"] = clean_condition(r.get("condition", ""))
    return rows


def make_prompt_effects(primary):
    by = {(r["model_label"], r["condition"]): r for r in primary}
    rows = []

    for model in sorted(set(r["model_label"] for r in primary)):
        imp = by.get((model, "implicit"))
        exp = by.get((model, "explicit"))
        if not imp or not exp:
            continue

        out = {"model_label": model}
        for metric in METRICS:
            try:
                out[f"{metric}_explicit_minus_implicit"] = round(
                    float(exp[f"{metric}_rate"]) - float(imp[f"{metric}_rate"]), 4
                )
            except Exception:
                out[f"{metric}_explicit_minus_implicit"] = ""
        rows.append(out)

    return rows


def make_qwen_family_difference(primary):
    by = {(r["model_label"], r["condition"]): r for r in primary}
    q3 = by.get(("Qwen-3B", "implicit"))
    q7 = by.get(("Qwen-7B", "implicit"))
    if not q3 or not q7:
        return []

    out = {"comparison": "Qwen-7B minus Qwen-3B under implicit"}
    for metric in METRICS:
        try:
            out[f"{metric}_q7_minus_q3"] = round(
                float(q7[f"{metric}_rate"]) - float(q3[f"{metric}_rate"]), 4
            )
        except Exception:
            out[f"{metric}_q7_minus_q3"] = ""
    return [out]


def make_figures(primary, by_risk):
    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        print("matplotlib unavailable; skipping figures:", e)
        return

    Path("figures").mkdir(exist_ok=True)

    implicit = [r for r in primary if r["condition"] == "implicit"]
    implicit = sorted(implicit, key=lambda r: r["model_label"])

    labels = [r["model_label"] for r in implicit]
    rates = [float(r["mirage_rate"]) for r in implicit]
    lows = [float(r["mirage_ci_low"]) for r in implicit]
    highs = [float(r["mirage_ci_high"]) for r in implicit]
    yerr = [[rates[i] - lows[i] for i in range(len(rates))], [highs[i] - rates[i] for i in range(len(rates))]]

    plt.figure()
    plt.bar(labels, rates, yerr=yerr, capsize=4)
    plt.ylabel("MIRAGE rate")
    plt.title("Phantom-0 implicit no-image MIRAGE by model")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig("figures/phantom0_mirage_implicit_by_model.png", dpi=200)
    plt.close()
    print("wrote figures/phantom0_mirage_implicit_by_model.png")

    models = sorted(set(r["model_label"] for r in primary))
    x = list(range(len(models)))
    width = 0.35
    imp_rates = []
    exp_rates = []

    for m in models:
        imp = next(r for r in primary if r["model_label"] == m and r["condition"] == "implicit")
        exp = next(r for r in primary if r["model_label"] == m and r["condition"] == "explicit")
        imp_rates.append(float(imp["mirage_rate"]))
        exp_rates.append(float(exp["mirage_rate"]))

    plt.figure()
    plt.bar([i - width / 2 for i in x], imp_rates, width, label="implicit")
    plt.bar([i + width / 2 for i in x], exp_rates, width, label="explicit")
    plt.xticks(x, models)
    plt.ylabel("MIRAGE rate")
    plt.title("Phantom-0 implicit vs explicit MIRAGE by model")
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig("figures/phantom0_mirage_prompt_effect.png", dpi=200)
    plt.close()
    print("wrote figures/phantom0_mirage_prompt_effect.png")

    risk_rows = sorted(by_risk, key=lambda r: (r["risk_level"], r["model_label"]))
    labels = [f"{r['risk_level']}\n{r['model_label']}" for r in risk_rows]
    rates = [float(r["mirage_rate"]) for r in risk_rows]

    plt.figure(figsize=(max(8, len(labels) * 0.6), 5))
    plt.bar(labels, rates)
    plt.ylabel("MIRAGE rate")
    plt.title("Phantom-0 implicit MIRAGE by risk level")
    plt.ylim(0, 1)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("figures/phantom0_mirage_by_risk_implicit.png", dpi=200)
    plt.close()
    print("wrote figures/phantom0_mirage_by_risk_implicit.png")


def main():
    rows = read_rows("annotations/phantom0_all_scored.csv")

    primary = summarize_group(rows, PRIMARY_GROUPS)
    implicit_rows = [r for r in rows if r["condition"] == "implicit"]

    by_risk = summarize_group(implicit_rows, RISK_GROUPS)
    by_question = summarize_group(implicit_rows, QUESTION_GROUPS)
    by_domain_category = summarize_group(implicit_rows, DOMAIN_CATEGORY_GROUPS)

    prompt_effects = make_prompt_effects(primary)
    qwen_family = make_qwen_family_difference(primary)

    write_csv("metrics/phantom0_primary_results.csv", primary)
    write_csv("metrics/phantom0_by_risk.csv", by_risk)
    write_csv("metrics/phantom0_by_question_type.csv", by_question)
    write_csv("metrics/phantom0_by_domain_category.csv", by_domain_category)
    write_csv("metrics/phantom0_prompt_effects.csv", prompt_effects)
    write_csv("metrics/phantom0_qwen_family_difference.csv", qwen_family)

    make_figures(primary, by_risk)

    print("\nPrimary summary:")
    for r in primary:
        print(
            r["model_label"],
            r["condition"],
            "N_valid=", r["n_valid"],
            "MIRAGE=", r["mirage_rate"],
            "Recognition=", r["recognition_rate"],
            "Hard=", r["hard_mirage_rate"],
            "Soft=", r["soft_mirage_rate"],
        )


if __name__ == "__main__":
    main()
