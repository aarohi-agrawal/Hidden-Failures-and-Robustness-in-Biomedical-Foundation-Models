import json
import random
from collections import defaultdict

INPUT = "outputs/scored/week5_smolvlm_256m_scored_v2.jsonl"

CONDITIONS = [
    "correct_image",
    "no_image",
    "blank_image",
    "far_mismatch",
    "hard_mismatch",
]

N_BOOT = 10000
SEED = 42

random.seed(SEED)

# Load scored rows
rows = []
with open(INPUT) as f:
    for line in f:
        if line.strip():
            rows.append(json.loads(line))

# Group by case_id.
# Each case should have one row per condition.
cases = defaultdict(dict)

for r in rows:
    case_id = r["case_id"]
    cases[case_id][r["condition"]] = r

# Keep only complete cases
complete_cases = [
    case_id
    for case_id, vals in cases.items()
    if all(c in vals for c in CONDITIONS)
]

print("WEEK 5 PAIRED BOOTSTRAP")
print("=" * 70)
print(f"Total rows: {len(rows)}")
print(f"Complete paired cases: {len(complete_cases)}")
print()

def accuracy(case_ids, condition):
    vals = [
        int(cases[c][condition]["correct"])
        for c in case_ids
    ]
    return sum(vals) / len(vals)

# Observed accuracies
print("Observed accuracy")
print("-" * 70)

for condition in CONDITIONS:
    acc = accuracy(complete_cases, condition)
    print(f"{condition:20s} {acc:.3f}")

print()

# Bootstrap confidence intervals
def bootstrap_accuracy(condition):
    estimates = []

    for _ in range(N_BOOT):
        sample = random.choices(
            complete_cases,
            k=len(complete_cases),
        )
        estimates.append(accuracy(sample, condition))

    estimates.sort()

    lo = estimates[int(0.025 * N_BOOT)]
    hi = estimates[int(0.975 * N_BOOT)]

    return lo, hi


print("95% bootstrap confidence intervals")
print("-" * 70)

for condition in CONDITIONS:
    lo, hi = bootstrap_accuracy(condition)
    print(f"{condition:20s} [{lo:.3f}, {hi:.3f}]")

print()

# Paired bootstrap differences relative to correct_image
baseline = "correct_image"

print("Paired differences vs correct_image")
print("-" * 70)

for condition in CONDITIONS:
    if condition == baseline:
        continue

    observed = (
        accuracy(complete_cases, condition)
        - accuracy(complete_cases, baseline)
    )

    diffs = []

    for _ in range(N_BOOT):
        sample = random.choices(
            complete_cases,
            k=len(complete_cases),
        )

        d = (
            accuracy(sample, condition)
            - accuracy(sample, baseline)
        )
        diffs.append(d)

    diffs.sort()

    lo = diffs[int(0.025 * N_BOOT)]
    hi = diffs[int(0.975 * N_BOOT)]

    # Two-sided bootstrap probability of difference crossing zero.
    p = 2 * min(
        sum(d <= 0 for d in diffs) / N_BOOT,
        sum(d >= 0 for d in diffs) / N_BOOT,
    )
    p = min(p, 1.0)

    print(
        f"{condition:20s} "
        f"diff={observed:+.3f} "
        f"CI=[{lo:+.3f}, {hi:+.3f}] "
        f"p~{p:.4f}"
    )
