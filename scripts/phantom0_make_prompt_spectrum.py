import csv
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

OLD = Path("annotations/phantom0_all_scored.csv")
MID = Path("annotations/phantom0_middle_scored.csv")
OUT = Path("metrics/phantom0_prompt_spectrum_results.csv")
FIG_DIR = Path("figures/comprehensive")

MODEL_ORDER = ["SmolVLM", "Qwen-3B", "Qwen-7B"]
COND_ORDER = ["implicit", "middle", "explicit"]
METRICS = ["mirage", "recognition", "explicit_abstention", "hard_mirage", "soft_mirage", "confident_answer", "hedged_answer"]

def model_label(name):
    if "SmolVLM" in name: return "SmolVLM"
    if "7B" in name: return "Qwen-7B"
    if "3B" in name or "Qwen" in name: return "Qwen-3B"
    return name

def cond_label(c):
    if c == "implicit_no_image": return "implicit"
    if c == "explicit_missing_image": return "explicit"
    if c == "evidence_check_no_image": return "middle"
    return c

def valid(r):
    return r.get("run_status") == "success" and r.get("judge_parse_success") == "yes" and r.get("response_mode") != "unscorable"

rows = []
for p in [OLD, MID]:
    for r in csv.DictReader(p.open(encoding="utf-8-sig")):
        r["model_label"] = model_label(r.get("model_name", ""))
        r["condition_spectrum"] = cond_label(r.get("condition", ""))
        rows.append(r)

groups = defaultdict(list)
for r in rows:
    if r["model_label"] in MODEL_ORDER and r["condition_spectrum"] in COND_ORDER:
        groups[(r["model_label"], r["condition_spectrum"])].append(r)

out = []
for model in MODEL_ORDER:
    for cond in COND_ORDER:
        g = groups[(model, cond)]
        v = [r for r in g if valid(r)]
        row = {
            "model_label": model,
            "condition": cond,
            "n_attempted": len(g),
            "n_valid": len(v),
            "n_excluded": len(g) - len(v),
        }
        for m in METRICS:
            row[m + "_rate"] = sum(1 for r in v if r.get(m) == "yes") / len(v) if v else ""
        out.append(row)

OUT.parent.mkdir(exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)

FIG_DIR.mkdir(parents=True, exist_ok=True)
colors = {"SmolVLM":"#9B51E0", "Qwen-3B":"#27AE60", "Qwen-7B":"#EB5757"}

def get(model, cond, metric):
    for r in out:
        if r["model_label"] == model and r["condition"] == cond:
            return float(r[metric + "_rate"])
    return np.nan

def plot(metric, title, fname, note, higher_good=False):
    x = np.arange(len(COND_ORDER))
    plt.figure(figsize=(8.5,5.3))
    ax = plt.gca()
    for model in MODEL_ORDER:
        vals = [get(model, c, metric) for c in COND_ORDER]
        ax.plot(x, vals, marker="o", linewidth=2.8, markersize=8, label=model, color=colors[model])
        for xi, yi in zip(x, vals):
            if not np.isnan(yi):
                ax.text(xi, min(1.05, yi + 0.025), f"{yi*100:.1f}%", ha="center", fontsize=8)
    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["Implicit", "Middle\nevidence-check", "Explicit"])
    ax.set_ylabel("Rate")
    ax.set_ylim(0, 1.08)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="Model")
    ax.text(0, -0.2, note, transform=ax.transAxes, fontsize=9, alpha=0.8)
    plt.tight_layout()
    plt.savefig(FIG_DIR / fname, dpi=220)
    plt.close()

plot("mirage", "Prompt spectrum: MIRAGE rate", "prompt_spectrum_mirage.png", "Middle prompt removes the literal 'No image is provided' line but keeps evidence-checking instructions.")
plot("recognition", "Prompt spectrum: missing-evidence recognition", "prompt_spectrum_recognition.png", "Higher recognition means the model acknowledges missing or insufficient visual evidence.")
plot("explicit_abstention", "Prompt spectrum: explicit abstention", "prompt_spectrum_abstention.png", "Higher abstention means the model refuses instead of giving an unsupported visual answer.")
plot("hard_mirage", "Prompt spectrum: hard MIRAGE", "prompt_spectrum_hard_mirage.png", "Hard MIRAGE = no acknowledgement + confident answer + specific visual claim.")
plot("confident_answer", "Prompt spectrum: confident answering", "prompt_spectrum_confident_answer.png", "Higher confident answering is riskier when visual evidence is unavailable.")

print("wrote", OUT, "rows=", len(out))
for r in out:
    print(r["model_label"], r["condition"], "n_valid=", r["n_valid"], "mirage=", r["mirage_rate"], "recognition=", r["recognition_rate"], "abstain=", r["explicit_abstention_rate"], "hard=", r["hard_mirage_rate"])
