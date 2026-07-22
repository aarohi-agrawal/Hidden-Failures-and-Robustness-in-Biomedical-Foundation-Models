import csv
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw

MANIFEST_DIR = Path("data/manifests")
BLANK_DIR = Path("data/generated/week3_blank_images")
DOCS_DIR = Path("docs")

SHARED_IMAGE_DIR = Path("/work/pi_cics-ur_umass_edu/mirage_shared/data/mmvp/MMVP Images")
QUESTIONS_CSV = Path("data/mmvp/Questions.csv")
WEEK2_EVAL = MANIFEST_DIR / "week2_mmvp_eval.csv"

MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
BLANK_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, columns):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def find_col(row, options):
    lower = {k.lower().strip(): k for k in row.keys()}

    for option in options:
        if option.lower() in lower:
            return lower[option.lower()]

    for key in row.keys():
        key_lower = key.lower().strip()
        for option in options:
            if option.lower() in key_lower:
                return key

    return None


def download_if_missing(url, dest):
    if dest.exists():
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {dest}")
    urllib.request.urlretrieve(url, dest)


def ensure_questions_csv():
    download_if_missing(
        "https://huggingface.co/datasets/MMVP/MMVP/resolve/main/Questions.csv",
        QUESTIONS_CSV,
    )


def ensure_image(source_id):
    image_path = SHARED_IMAGE_DIR / f"{source_id}.jpg"

    download_if_missing(
        f"https://huggingface.co/datasets/MMVP/MMVP/resolve/main/MMVP%20Images/{source_id}.jpg",
        image_path,
    )

    return image_path


def main():
    ensure_questions_csv()

    # Step 1: record Week 2 MMVP IDs so Week 3 avoids them.
    week2_rows = read_csv(WEEK2_EVAL)
    week2_used = sorted(
        {
            str(row.get("source_id", "")).strip()
            for row in week2_rows
            if str(row.get("source_id", "")).strip()
        }
    )

    write_csv(
        MANIFEST_DIR / "week2_mmvp_used_ids.csv",
        [{"source_id": source_id} for source_id in week2_used],
        ["source_id"],
    )

    # Step 2: select 16 new MMVP examples.
    ensure_questions_csv()
    question_rows = read_csv(QUESTIONS_CSV)
    sample = question_rows[0]

    id_col = find_col(sample, ["Index", "id", "source_id", "question_id"])
    question_col = find_col(sample, ["Question", "question", "prompt"])
    answer_col = find_col(sample, ["Correct Answer", "answer", "gold_answer", "label"])
    category_col = find_col(sample, ["category", "visual_pattern", "type"])

    if not id_col or not question_col or not answer_col:
        raise RuntimeError(f"Could not identify columns in Questions.csv: {list(sample.keys())}")

    candidates = []

    for row in question_rows:
        source_id = str(row.get(id_col, "")).strip()
        question = str(row.get(question_col, "")).strip()
        gold_answer = str(row.get(answer_col, "")).strip()
        category = str(row.get(category_col, "unknown")).strip() if category_col else "unknown"

        if not source_id or not question or not gold_answer:
            continue

        if source_id in week2_used:
            continue

        candidates.append(
            {
                "source_id": source_id,
                "dataset": "MMVP",
                "category": category or "unknown",
                "question": question,
                "gold_answer": gold_answer,
            }
        )

    candidates = sorted(
        candidates,
        key=lambda x: int(x["source_id"]) if str(x["source_id"]).isdigit() else x["source_id"],
    )

    # Spread across the dataset instead of taking adjacent rows.
    indexes = [round(i * (len(candidates) - 1) / 15) for i in range(16)]
    selected = [candidates[i] for i in indexes]

    seed_rows = []

    for i, row in enumerate(selected, start=1):
        source_id = row["source_id"]
        image_abs = ensure_image(source_id)

        with Image.open(image_abs) as img:
            width, height = img.size

        bundle_id = f"mmvp_w3_{i:03d}"
        original_rel = f"data/mmvp/MMVP Images/{source_id}.jpg"

        seed_rows.append(
            {
                "bundle_id": bundle_id,
                "source_id": source_id,
                "dataset": "MMVP",
                "category": row["category"],
                "question": row["question"],
                "gold_answer": row["gold_answer"],
                "original_image_path": original_rel,
                "selection_notes": f"Week 2 examples excluded; image opened successfully ({width}x{height}).",
            }
        )

    write_csv(
        MANIFEST_DIR / "week3_mmvp_seed.csv",
        seed_rows,
        [
            "bundle_id",
            "source_id",
            "dataset",
            "category",
            "question",
            "gold_answer",
            "original_image_path",
            "selection_notes",
        ],
    )

    # Step 3: create matched blank images.
    blank_info = {}

    for row in seed_rows:
        source_id = row["source_id"]
        bundle_id = row["bundle_id"]
        image_abs = ensure_image(source_id)

        with Image.open(image_abs) as img:
            width, height = img.size

        blank_path = BLANK_DIR / f"{bundle_id}_blank.png"
        Image.new("RGB", (width, height), (255, 255, 255)).save(blank_path)

        blank_info[bundle_id] = {
            "path": str(blank_path),
            "width": width,
            "height": height,
            "pixel_value": "RGB(255,255,255)",
        }

    # Step 4: create deterministic mismatches using +8 rotation.
    mismatch_rows = []
    n = len(seed_rows)

    for i, row in enumerate(seed_rows):
        mismatch = seed_rows[(i + n // 2) % n]

        mismatch_rows.append(
            {
                "bundle_id": row["bundle_id"],
                "question_source_id": row["source_id"],
                "correct_image_source_id": row["source_id"],
                "mismatched_image_source_id": mismatch["source_id"],
                "mismatched_image_path": f"data/mmvp/MMVP Images/{mismatch['source_id']}.jpg",
                "mismatch_reviewed": "no",
                "review_notes": "Deterministic +8 rotation. Student A must review before handoff.",
            }
        )

    write_csv(
        MANIFEST_DIR / "week3_mismatch_map.csv",
        mismatch_rows,
        [
            "bundle_id",
            "question_source_id",
            "correct_image_source_id",
            "mismatched_image_source_id",
            "mismatched_image_path",
            "mismatch_reviewed",
            "review_notes",
        ],
    )

    # Step 5: create 64-row eval manifest.
    mismatch_by_bundle = {row["bundle_id"]: row for row in mismatch_rows}
    eval_rows = []

    for row in seed_rows:
        bundle_id = row["bundle_id"]
        correct_path = row["original_image_path"]
        blank_path = blank_info[bundle_id]["path"]
        mismatch = mismatch_by_bundle[bundle_id]

        base = {
            "bundle_id": bundle_id,
            "source_id": row["source_id"],
            "dataset": "MMVP",
            "category": row["category"],
            "question": row["question"],
            "gold_answer": row["gold_answer"],
            "correct_image_path": correct_path,
            "prompt_version": "mmvp_evidence_integrity_v1",
            "include_in_eval": "yes",
            "exclusion_reason": "",
        }

        eval_rows.append(
            {
                **base,
                "case_id": f"{bundle_id}_image_present",
                "condition": "image_present",
                "image_path": correct_path,
                "mismatch_source_id": "",
                "notes": "Correct MMVP image is provided.",
            }
        )

        eval_rows.append(
            {
                **base,
                "case_id": f"{bundle_id}_no_image",
                "condition": "no_image",
                "image_path": "",
                "mismatch_source_id": "",
                "notes": "No image should be passed to the model.",
            }
        )

        eval_rows.append(
            {
                **base,
                "case_id": f"{bundle_id}_blank_image",
                "condition": "blank_image",
                "image_path": blank_path,
                "mismatch_source_id": "",
                "notes": f"Matched blank image, {blank_info[bundle_id]['width']}x{blank_info[bundle_id]['height']}, RGB(255,255,255).",
            }
        )

        eval_rows.append(
            {
                **base,
                "case_id": f"{bundle_id}_mismatched_image",
                "condition": "mismatched_image",
                "image_path": mismatch["mismatched_image_path"],
                "mismatch_source_id": mismatch["mismatched_image_source_id"],
                "notes": f"Mismatched image from source_id {mismatch['mismatched_image_source_id']}. Review status: no.",
            }
        )

    eval_columns = [
        "case_id",
        "bundle_id",
        "source_id",
        "dataset",
        "category",
        "question",
        "gold_answer",
        "condition",
        "image_path",
        "correct_image_path",
        "mismatch_source_id",
        "prompt_version",
        "include_in_eval",
        "exclusion_reason",
        "notes",
    ]

    write_csv(MANIFEST_DIR / "week3_mmvp_eval.csv", eval_rows, eval_columns)

    # Contact sheet for manual mismatch review.
    contact_sheet = DOCS_DIR / "week3_mismatch_review_contact_sheet.png"
    sheet = Image.new("RGB", (900, 260 * len(mismatch_rows)), "white")
    draw = ImageDraw.Draw(sheet)
    seed_by_source = {row["source_id"]: row for row in seed_rows}

    for i, mismatch in enumerate(mismatch_rows):
        y = i * 260
        question_sid = mismatch["question_source_id"]
        mismatch_sid = mismatch["mismatched_image_source_id"]

        for x, sid, label in [
            (10, question_sid, "correct image"),
            (230, mismatch_sid, "mismatched image"),
        ]:
            with Image.open(ensure_image(sid)) as img:
                img.thumbnail((180, 180))
                sheet.paste(img.convert("RGB"), (x, y + 40))

            draw.text((x, y + 225), label, fill="black")

        question = seed_by_source[question_sid]["question"][:120]

        draw.text(
            (10, y + 5),
            f"{mismatch['bundle_id']} | question source {question_sid} | mismatch source {mismatch_sid}",
            fill="black",
        )
        draw.text((450, y + 45), f"Question: {question}", fill="black")
        draw.text((450, y + 100), "Review: mismatch should not answer the question.", fill="black")

    sheet.save(contact_sheet)

    # Validation.
    validation_errors = []

    if len(seed_rows) != 16:
        validation_errors.append(f"Expected 16 seed bundles, found {len(seed_rows)}")

    if len(eval_rows) != 64:
        validation_errors.append(f"Expected 64 eval rows, found {len(eval_rows)}")

    for row in eval_rows:
        if row["condition"] == "no_image" and row["image_path"]:
            validation_errors.append(f"{row['case_id']} no_image has non-empty image_path")

        if row["condition"] != "no_image":
            if not row["image_path"]:
                validation_errors.append(f"{row['case_id']} missing image_path")
            elif not Path(row["image_path"]).exists():
                validation_errors.append(f"{row['case_id']} image path does not exist: {row['image_path']}")

    for mismatch in mismatch_rows:
        if mismatch["question_source_id"] == mismatch["mismatched_image_source_id"]:
            validation_errors.append(f"{mismatch['bundle_id']} uses its own image as mismatch")

    doc = f"""# Week 3 Data Review

## Files created

- data/manifests/week2_mmvp_used_ids.csv
- data/manifests/week3_mmvp_seed.csv
- data/manifests/week3_mismatch_map.csv
- data/manifests/week3_mmvp_eval.csv
- data/generated/week3_blank_images/
- docs/week3_mismatch_review_contact_sheet.png

## Summary

- New bundles: {len(seed_rows)}
- Manifest rows: {len(eval_rows)}
- Conditions: image_present, no_image, blank_image, mismatched_image
- Prompt version: mmvp_evidence_integrity_v1

## Selection procedure

Week 2 source IDs were excluded. Sixteen new examples were selected across the MMVP source-ID range rather than by taking adjacent rows.

## Shared image path

/work/pi_cics-ur_umass_edu/mirage_shared/data/mmvp/MMVP Images

## Blank images

Blank images were generated with the same width and height as the original image whenever practical.

Folder:

data/generated/week3_blank_images/

Pixel value:

RGB(255,255,255)

## Mismatch construction

Mismatched images were assigned using a deterministic +8 rotation across the 16 selected bundles.

Review contact sheet:

docs/week3_mismatch_review_contact_sheet.png

## Validation notes

Validation errors before manual mismatch review:

{chr(10).join("- " + e for e in validation_errors) if validation_errors else "- None"}

Manual mismatch review still needs to be marked in data/manifests/week3_mismatch_map.csv before final handoff.
"""

    (DOCS_DIR / "week3_data_review.md").write_text(doc, encoding="utf-8")

    print("Created Week 3 Student A files.")
    print("Bundles:", len(seed_rows))
    print("Eval rows:", len(eval_rows))
    print("Validation errors:", len(validation_errors))

    for error in validation_errors[:20]:
        print("-", error)

    print("")
    print("Next: open docs/week3_mismatch_review_contact_sheet.png and review mismatches.")


if __name__ == "__main__":
    main()