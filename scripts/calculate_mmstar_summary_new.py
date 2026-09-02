import pandas as pd
import numpy as np
from pathlib import Path

INPUT_FILE = Path("metrics/mmstar_120results_long.csv")
OUTPUT_FILE = Path("metrics/mmstar_summary.csv")

N_BOOTSTRAP = 10000
SEED = 42

CONDITIONS = [
    "correct_image",
    "no_image",
    "blank_image",
    "far_mismatch",
    "hard_mismatch",
]

INVALID_CONDITIONS = [
    "no_image",
    "blank_image",
    "far_mismatch",
    "hard_mismatch",
]

DECISIONS = {"A", "B", "C", "D"}


def load_data():
    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "source_id",
        "bundle_id",
        "model_name",
        "condition",
        "official_gold",
        "decision",
        "response_mode",
        "evidence_issue_stated",
    ]

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for col in [
        "model_name",
        "condition",
        "official_gold",
        "decision",
        "response_mode",
        "evidence_issue_stated",
    ]:
        df[col] = df[col].astype("string").str.strip()

    df["official_gold"] = df["official_gold"].str.upper()
    df["decision"] = df["decision"].str.upper()
    df["evidence_issue_stated"] = df["evidence_issue_stated"].str.lower()

    return df


def validate_input(df):
    models = sorted(df["model_name"].dropna().unique())

    print(f"Loaded {len(df)} rows.")
    print(f"Found {len(models)} models:")

    for model in models:
        model_df = df[df["model_name"] == model]
        print(
            f"  {model}: "
            f"{len(model_df)} rows, "
            f"{model_df['source_id'].nunique()} source IDs"
        )

    if len(models) != 3:
        raise ValueError(f"Expected 3 models, found {len(models)}")

    if len(df) != 900:
        raise ValueError(f"Expected 900 total rows, found {len(df)}")

    for model in models:
        model_df = df[df["model_name"] == model]

        if len(model_df) != 300:
            raise ValueError(
                f"{model}: expected 300 rows, found {len(model_df)}"
            )

        if model_df["source_id"].nunique() != 60:
            raise ValueError(
                f"{model}: expected 60 source IDs, "
                f"found {model_df['source_id'].nunique()}"
            )

        pair_counts = (
            model_df.groupby(["source_id", "condition"]).size()
        )
        bad_pairs = pair_counts[pair_counts != 1]

        if len(bad_pairs) > 0:
            print("\nDuplicate source_id/condition pairs:")
            print(bad_pairs)
            raise ValueError(
                f"{model}: duplicate or malformed source_id/condition pairs."
            )

        source_condition_counts = (
            model_df.groupby("source_id")["condition"].nunique()
        )
        if not (source_condition_counts == 5).all():
            bad_sources = source_condition_counts[
                source_condition_counts != 5
            ]
            print("\nInvalid source IDs:")
            print(bad_sources)
            raise ValueError(
                f"{model}: not every source ID has all five conditions."
            )

        condition_counts = model_df["condition"].value_counts()
        for condition in CONDITIONS:
            count = condition_counts.get(condition, 0)
            if count != 60:
                raise ValueError(
                    f"{model}: {condition} has {count} rows instead of 60."
                )

    print("Input validation passed.")


def correct_image_accuracy(df):
    x = df[df["condition"] == "correct_image"]
    return (x["decision"] == x["official_gold"]).mean()


def confident_valid_image_error_rate(df):
    x = df[df["condition"] == "correct_image"]
    return (
        (x["decision"] != x["official_gold"])
        & (x["response_mode"] == "confident_answer")
    ).mean()


def original_gold_match(df, condition):
    x = df[df["condition"] == condition]
    return (x["decision"] == x["official_gold"]).mean()


def evidence_dependence_gap(df, condition):
    return correct_image_accuracy(df) - original_gold_match(df, condition)


def appropriate_response(df, condition):
    x = df[df["condition"] == condition]
    return (
        x["decision"].eq("ABSTAIN")
        & x["evidence_issue_stated"].ne("none")
    ).mean()


def blindness(df, condition):
    x = df[df["condition"] == condition]
    return (
        x["decision"].isin(DECISIONS)
        & x["evidence_issue_stated"].eq("none")
    ).mean()


def paired_conditions(df, condition):
    correct = (
        df[df["condition"] == "correct_image"][
            ["source_id", "decision"]
        ]
        .rename(columns={"decision": "correct_decision"})
    )

    invalid = (
        df[df["condition"] == condition][
            ["source_id", "decision", "evidence_issue_stated"]
        ]
        .rename(
            columns={
                "decision": "invalid_decision",
                "evidence_issue_stated": "invalid_evidence_issue",
            }
        )
    )

    paired = correct.merge(
        invalid,
        on="source_id",
        how="inner",
        validate="one_to_one",
    )

    if len(paired) != 60:
        raise ValueError(
            f"{condition}: expected 60 paired rows, found {len(paired)}"
        )

    return paired


def answer_invariance(df, condition):
    paired = paired_conditions(df, condition)
    return (
        paired["correct_decision"] == paired["invalid_decision"]
    ).mean()


def appropriate_condition_sensitivity(df, condition):
    paired = paired_conditions(df, condition)
    return (
        paired["correct_decision"].isin(DECISIONS)
        & paired["invalid_decision"].eq("ABSTAIN")
        & paired["invalid_evidence_issue"].ne("none")
    ).mean()


def print_raw_diagnostics(model_df):
    print()
    print("RAW COUNTS")
    print("-" * 60)

    correct = model_df[model_df["condition"] == "correct_image"]
    n_correct = len(correct)

    correct_n = (
        correct["decision"] == correct["official_gold"]
    ).sum()

    confident_error_n = (
        (correct["decision"] != correct["official_gold"])
        & (correct["response_mode"] == "confident_answer")
    ).sum()

    print(f"Correct-image accuracy: {correct_n}/{n_correct}")
    print(
        f"Confident valid-image error: "
        f"{confident_error_n}/{n_correct}"
    )

    for condition in INVALID_CONDITIONS:
        x = model_df[model_df["condition"] == condition]

        gold_n = (
            x["decision"] == x["official_gold"]
        ).sum()

        appropriate_n = (
            x["decision"].eq("ABSTAIN")
            & x["evidence_issue_stated"].ne("none")
        ).sum()

        blindness_n = (
            x["decision"].isin(DECISIONS)
            & x["evidence_issue_stated"].eq("none")
        ).sum()

        paired = paired_conditions(model_df, condition)

        invariance_n = (
            paired["correct_decision"]
            == paired["invalid_decision"]
        ).sum()

        sensitivity_n = (
            paired["correct_decision"].isin(DECISIONS)
            & paired["invalid_decision"].eq("ABSTAIN")
            & paired["invalid_evidence_issue"].ne("none")
        ).sum()

        print()
        print(condition)
        print(f"  Gold match: {gold_n}/60")
        print(f"  Appropriate response: {appropriate_n}/60")
        print(f"  Blindness: {blindness_n}/60")
        print(f"  Invariance: {invariance_n}/60")
        print(f"  Appropriate sensitivity: {sensitivity_n}/60")


def bootstrap_bundle_metric(df, metric_fn, seed):
    rng = np.random.default_rng(seed)

    source_ids = df["source_id"].unique()

    if len(source_ids) != 60:
        raise ValueError(
            f"Bootstrap expected 60 source IDs, found {len(source_ids)}"
        )

    estimate = metric_fn(df)

    bundles = {
        source_id: group.copy()
        for source_id, group in df.groupby("source_id")
    }

    bootstrap_values = []

    for _ in range(N_BOOTSTRAP):
        sampled_ids = rng.choice(
            source_ids,
            size=60,
            replace=True,
        )

        sampled_chunks = []

        for draw_id, source_id in enumerate(sampled_ids):
            bundle = bundles[source_id].copy()
            bundle["_bootstrap_source_id"] = draw_id
            sampled_chunks.append(bundle)

        sampled = pd.concat(sampled_chunks, ignore_index=True)

        sampled["source_id"] = sampled["_bootstrap_source_id"]

        value = metric_fn(sampled)
        bootstrap_values.append(value)

    bootstrap_values = np.asarray(bootstrap_values, dtype=float)

    ci_low = np.percentile(bootstrap_values, 2.5)
    ci_high = np.percentile(bootstrap_values, 97.5)

    return estimate, ci_low, ci_high


def main():
    print(f"Loading {INPUT_FILE}...")

    df = load_data()
    validate_input(df)

    models = sorted(df["model_name"].unique())
    rows = []
    metric_counter = 0

    for model in models:
        print()
        print("=" * 70)
        print(f"MODEL: {model}")
        print("=" * 70)

        model_df = df[df["model_name"] == model].copy()

        print_raw_diagnostics(model_df)

        metrics = [
            (
                "correct_image_accuracy",
                "correct_image",
                lambda d: correct_image_accuracy(d),
            ),
            (
                "confident_valid_image_error_rate",
                "correct_image",
                lambda d: confident_valid_image_error_rate(d),
            ),
        ]

        for condition in INVALID_CONDITIONS:
            metrics.append(
                (
                    "original_gold_match",
                    condition,
                    lambda d, c=condition:
                        original_gold_match(d, c),
                )
            )

            metrics.append(
                (
                    "evidence_dependence_gap",
                    condition,
                    lambda d, c=condition:
                        evidence_dependence_gap(d, c),
                )
            )

        for condition in INVALID_CONDITIONS:
            metrics.append(
                (
                    "appropriate_response",
                    condition,
                    lambda d, c=condition:
                        appropriate_response(d, c),
                )
            )

        metrics.extend([
            (
                "blank_blindness",
                "blank_image",
                lambda d:
                    blindness(d, "blank_image"),
            ),
            (
                "far_mismatch_blindness",
                "far_mismatch",
                lambda d:
                    blindness(d, "far_mismatch"),
            ),
            (
                "hard_mismatch_blindness",
                "hard_mismatch",
                lambda d:
                    blindness(d, "hard_mismatch"),
            ),
        ])

        for condition in INVALID_CONDITIONS:
            metrics.append(
                (
                    "answer_invariance",
                    condition,
                    lambda d, c=condition:
                        answer_invariance(d, c),
                )
            )

            metrics.append(
                (
                    "appropriate_condition_sensitivity",
                    condition,
                    lambda d, c=condition:
                        appropriate_condition_sensitivity(d, c),
                )
            )

        for metric_name, condition, metric_fn in metrics:
            print(
                f"\n  {metric_name} ({condition})..."
            )

            estimate, ci_low, ci_high = bootstrap_bundle_metric(
                model_df,
                metric_fn,
                seed=SEED + metric_counter,
            )

            metric_counter += 1

            print(
                f"    estimate = {estimate:.4f} "
                f"| 95% CI = [{ci_low:.4f}, {ci_high:.4f}]"
            )

            rows.append({
                "model_name": model,
                "metric": metric_name,
                "condition": condition,
                "n": 60,
                "estimate": estimate,
                "ci_95_low": ci_low,
                "ci_95_high": ci_high,
            })

    summary = pd.DataFrame(rows)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT_FILE, index=False)

    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)
    print(f"Saved {len(summary)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
