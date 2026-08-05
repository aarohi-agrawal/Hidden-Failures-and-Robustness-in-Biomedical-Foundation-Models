from pathlib import Path
import pandas as pd


SEED = Path("data/manifests/week5_evidence_ladder_seed.csv")
FAR = Path("data/manifests/week5_far_mismatch_map.csv")
HARD = Path("data/manifests/week5_hard_mismatch_map.csv")
BLANK_REPORT = Path(
    "data/generated/week5_blank_images/week5_blank_image_report.csv"
)

OUTPUT = Path(
    "data/manifests/week5_evidence_ladder_eval.csv"
)


seed = pd.read_csv(SEED)
far = pd.read_csv(FAR)
hard = pd.read_csv(HARD)
blank = pd.read_csv(BLANK_REPORT)


rows = []


for idx, row in seed.reset_index(drop=True).iterrows():

    case_id = int(row.case_id)

    blank_file = blank.loc[
        blank["case_id"] == case_id,
        "filename"
    ].iloc[0]


    # 1. Correct image
    rows.append({
        "case_id": case_id,
        "category": row.category,
        "gold_answer": row.gold_answer,
        "condition": "correct_image",
        "image_id": case_id,
        "mismatch_source_id": "",
        "difficulty_rating": "",
        "notes": "Original MMVP image"
    })


    # 2. No image
    rows.append({
        "case_id": case_id,
        "category": row.category,
        "gold_answer": row.gold_answer,
        "condition": "no_image",
        "image_id": "",
        "mismatch_source_id": "",
        "difficulty_rating": "",
        "notes": "Image removed"
    })


    # 3. Blank image
    rows.append({
        "case_id": case_id,
        "category": row.category,
        "gold_answer": row.gold_answer,
        "condition": "blank_image",
        "image_id": blank_file,
        "mismatch_source_id": "",
        "difficulty_rating": "",
        "notes": "Matched blank image"
    })


    # 4. Far mismatch
    far_row = far[far.source_id == case_id].iloc[0]

    rows.append({
        "case_id": case_id,
        "category": row.category,
        "gold_answer": row.gold_answer,
        "condition": "far_mismatch",
        "image_id": far_row.mismatch_source_id,
        "mismatch_source_id": far_row.mismatch_source_id,
        "difficulty_rating": "",
        "notes": far_row.reason
    })


    # 5. Hard mismatch
    hard_row = hard[hard.source_id == case_id].iloc[0]

    rows.append({
        "case_id": case_id,
        "category": row.category,
        "gold_answer": row.gold_answer,
        "condition": "hard_mismatch",
        "image_id": hard_row.mismatch_source_id,
        "mismatch_source_id": hard_row.mismatch_source_id,
        "difficulty_rating": hard_row.difficulty_rating,
        "notes": hard_row.reason
    })


result = pd.DataFrame(rows)

assert len(result) == 200, f"Expected 200 rows, got {len(result)}"

assert (
    result.groupby("case_id").size() == 5
).all(), "Every case must have exactly 5 conditions"


result.to_csv(OUTPUT, index=False)


print(f"Created {len(result)} rows")
print(f"Saved to {OUTPUT}")