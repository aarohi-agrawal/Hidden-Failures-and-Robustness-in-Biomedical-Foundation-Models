import csv
from pathlib import Path

primary = list(csv.DictReader(open("metrics/phantom0_primary_results.csv", encoding="utf-8-sig")))
prompt_effects = list(csv.DictReader(open("metrics/phantom0_prompt_effects.csv", encoding="utf-8-sig")))
qwen_family = list(csv.DictReader(open("metrics/phantom0_qwen_family_difference.csv", encoding="utf-8-sig")))

def pct(x):
    if x == "" or x is None:
        return ""
    return f"{float(x)*100:.1f}%"

lines = []
lines.append("# Phantom-0 Week 5 Meeting Summary\n")
lines.append("## Status\n")
lines.append("- Full raw output set complete: 1,200 total outputs.")
lines.append("- Models: SmolVLM, Qwen-3B, Qwen-7B.")
lines.append("- Conditions: implicit no-image and explicit missing-image.")
lines.append("- Automatic judge completed with one retry pass.")
lines.append("- 1,196 / 1,200 rows parsed successfully.")
lines.append("- 4 judge parse failures remain documented in `annotations/phantom0_judge_parse_failures.csv`.")
lines.append("- Results below are automatic-judge results and still require human-audit validation.\n")

lines.append("## Primary Results\n")
lines.append("| Model | Condition | N valid | MIRAGE | Recognition | Abstain | Hard MIRAGE | Soft MIRAGE |")
lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
for r in primary:
    lines.append(
        f"| {r['model_label']} | {r['condition']} | {r['n_valid']} | "
        f"{pct(r['mirage_rate'])} | {pct(r['recognition_rate'])} | "
        f"{pct(r['explicit_abstention_rate'])} | {pct(r['hard_mirage_rate'])} | {pct(r['soft_mirage_rate'])} |"
    )

lines.append("\n## Prompt Effects")
lines.append("These are explicit minus implicit differences. Negative MIRAGE means the explicit missing-image prompt lowered MIRAGE.\n")
lines.append("| Model | MIRAGE Δ | Recognition Δ | Abstain Δ | Hard MIRAGE Δ | Soft MIRAGE Δ |")
lines.append("|---|---:|---:|---:|---:|---:|")
for r in prompt_effects:
    lines.append(
        f"| {r['model_label']} | {pct(r['mirage_explicit_minus_implicit'])} | "
        f"{pct(r['recognition_explicit_minus_implicit'])} | {pct(r['explicit_abstention_explicit_minus_implicit'])} | "
        f"{pct(r['hard_mirage_explicit_minus_implicit'])} | {pct(r['soft_mirage_explicit_minus_implicit'])} |"
    )

lines.append("\n## Qwen Family Comparison")
if qwen_family:
    r = qwen_family[0]
    lines.append("- Comparison: Qwen-7B minus Qwen-3B under implicit condition.")
    lines.append(f"- MIRAGE difference: {pct(r['mirage_q7_minus_q3'])}")
    lines.append(f"- Recognition difference: {pct(r['recognition_q7_minus_q3'])}")
    lines.append(f"- Hard MIRAGE difference: {pct(r['hard_mirage_q7_minus_q3'])}")
    lines.append(f"- Soft MIRAGE difference: {pct(r['soft_mirage_q7_minus_q3'])}")
else:
    lines.append("- Qwen family comparison not available.")

lines.append("\n## Caveats")
lines.append("- These are not final claims until the human audit agreement is computed.")
lines.append("- Do not claim that scale caused any improvement.")
lines.append("- Do not describe Qwen as perfect; use the exact rates.")
lines.append("- The explicit condition is a control, not the primary MIRAGE replication condition.")

Path("reports").mkdir(exist_ok=True)
Path("reports/luke_phantom0_meeting_summary.md").write_text("\n".join(lines), encoding="utf-8")
print("wrote reports/luke_phantom0_meeting_summary.md")
