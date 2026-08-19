import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoProcessor


PROMPT_VERSION = "mmvp_evidence_integrity_v1"

IMAGE_CONDITIONS = {
    "correct_image",
    "blank_image",
    "far_mismatch",
    "hard_mismatch",
}


def load_model(model_name: str, model_revision: str):
    """Load the model using the appropriate model class."""

    if "Qwen2.5-VL" in model_name:
        from transformers import Qwen2_5_VLForConditionalGeneration

        return Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            revision=model_revision,
            torch_dtype="auto",
            device_map="auto",
        )

    from transformers import AutoModelForImageTextToText

    return AutoModelForImageTextToText.from_pretrained(
        model_name,
        revision=model_revision,
        torch_dtype="auto",
        device_map="auto",
    )


def load_questions(path: str):
    """Load official MMVP questions."""

    questions = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            index = int(row["Index"])
            questions[index] = {
                "question": row["Question"].strip(),
                "options": row["Options"].strip(),
                "gold_answer": row["Correct Answer"].strip(),
            }

    return questions


def load_prompt(question: str, options: str):
    """Load the standardized evidence-integrity prompt."""

    prompt_file = Path("prompts") / f"{PROMPT_VERSION}.txt"

    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}"
        )

    with open(prompt_file, "r", encoding="utf-8") as file:
        template = file.read()

    prompt = template.format(
        question=question,
        options=options,
    )

    return prompt, str(prompt_file)


def resolve_image_path(row):
    """Resolve the image path for a Week 5 condition."""

    condition = row["condition"].strip()
    image_id = row.get("image_id", "").strip()

    if condition == "no_image":
        return ""

    if not image_id:
        raise ValueError(
            f"Missing image_id for condition={condition}"
        )

    if condition == "blank_image":
        path = Path(
            "data/generated/week5_blank_images"
        ) / image_id

    elif condition in {
        "correct_image",
        "far_mismatch",
        "hard_mismatch",
    }:
        path = (
            Path("data/mmvp/MMVP Images")
            / f"{image_id}.jpg"
        )

    else:
        raise ValueError(
            f"Unknown condition: {condition}"
        )

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {path}"
        )

    return str(path)


def validate_row(row, questions):
    """Validate one Week 5 manifest row."""

    condition = row.get("condition", "").strip()

    allowed = IMAGE_CONDITIONS | {"no_image"}

    if condition not in allowed:
        raise ValueError(
            f"Unknown condition: {condition}"
        )

    case_id = int(row["case_id"])

    if case_id not in questions:
        raise ValueError(
            f"case_id {case_id} not found in Questions.csv"
        )

    if not row.get("gold_answer", "").strip():
        raise ValueError(
            f"Missing gold_answer for case_id={case_id}"
        )

    image_path = resolve_image_path(row)

    if condition == "no_image" and image_path:
        raise ValueError(
            "no_image must not have an image path"
        )

    if condition in {
        "far_mismatch",
        "hard_mismatch",
    }:
        if not row.get("mismatch_source_id", "").strip():
            raise ValueError(
                f"{condition} requires mismatch_source_id"
            )

    return image_path


def build_messages(condition, prompt, image_path):
    """Build model input for one evidence condition."""

    if condition in IMAGE_CONDITIONS:
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image_path,
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

    if condition == "no_image":
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

    raise ValueError(
        f"Unknown condition: {condition}"
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--manifest",
        required=True,
    )

    parser.add_argument(
        "--questions",
        default="data/Questions.csv",
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--model",
        required=True,
    )

    parser.add_argument(
        "--model-revision",
        default="main",
    )

    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=128,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
    )

    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    questions_path = Path(args.questions)
    output_path = Path(args.output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    questions = load_questions(
        str(questions_path)
    )

    model_name = args.model
    model_revision = args.model_revision

    generation_parameters = {
        "temperature": 0.0,
        "do_sample": False,
        "max_new_tokens": args.max_new_tokens,
    }

    print(f"Manifest: {manifest_path}")
    print(f"Questions: {questions_path}")
    print(f"Output: {output_path}")
    print(f"Model: {model_name}")
    print(f"Model revision: {model_revision}")
    print(f"Prompt version: {PROMPT_VERSION}")
    print(f"Generation parameters: {generation_parameters}")
    print(
        "CUDA available: "
        f"{torch.cuda.is_available()}"
    )

    processor = AutoProcessor.from_pretrained(
        model_name,
        revision=model_revision,
    )

    model = load_model(
        model_name,
        model_revision,
    )

    start_time = time.perf_counter()

    rows_attempted = 0
    rows_written = 0
    rows_failed = 0

    with open(
        manifest_path,
        newline="",
        encoding="utf-8",
    ) as manifest_file, open(
        output_path,
        "a",
        encoding="utf-8",
    ) as output_file:

        reader = csv.DictReader(manifest_file)

        for row_index, row in enumerate(reader):

            if row_index < args.start:
               continue

            if (
                args.limit is not None
                and rows_attempted >= args.limit
            ):
                break

            rows_attempted += 1

            condition = row.get(
                "condition",
                "",
            ).strip()

            case_id = int(row["case_id"])

            raw_response = ""
            error = None
            image_path = ""
            prompt_file_used = ""

            try:

                image_path = validate_row(
                    row,
                    questions,
                )

                q = questions[case_id]

                # The frozen Week 5 manifest is authoritative
                # for the gold answer. Questions.csv supplies
                # the question/options text.
                question = q["question"]
                options = q["options"]

                if (
                    row["gold_answer"].strip()
                    != q["gold_answer"]
                ):
                    raise ValueError(
                        f"Gold mismatch for case_id={case_id}: "
                        f"manifest={row['gold_answer']} "
                        f"Questions.csv={q['gold_answer']}"
                    )

                prompt, prompt_file_used = load_prompt(
                    question,
                    options,
                )

                messages = build_messages(
                    condition,
                    prompt,
                    image_path,
                )

                text = processor.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )

                if condition in IMAGE_CONDITIONS:

                    from qwen_vl_utils import (
                        process_vision_info,
                    )

                    (
                        image_inputs,
                        video_inputs,
                    ) = process_vision_info(messages)

                    inputs = processor(
                        text=[text],
                        images=image_inputs,
                        videos=video_inputs,
                        padding=True,
                        return_tensors="pt",
                    )

                else:

                    inputs = processor(
                        text=[text],
                        padding=True,
                        return_tensors="pt",
                    )

                try:
                    inputs = inputs.to(model.device)
                except Exception:
                    pass

                with torch.no_grad():

                    generated_ids = model.generate(
                        **inputs,
                        max_new_tokens=args.max_new_tokens,
                        do_sample=False,
                    )

                generated_ids = generated_ids[
                    :,
                    inputs["input_ids"].shape[1]:,
                ]

                raw_response = processor.batch_decode(
                    generated_ids,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=False,
                )[0]

            except Exception as exception:

                raw_response = ""
                error = str(exception)
                rows_failed += 1

            output = {
                "run_id": (
                    f"week5_"
                    f"{model_name.split('/')[-1]}_"
                    f"{rows_attempted:03d}"
                ),
                "case_id": row.get(
                    "case_id",
                    "",
                ),
                "category": row.get(
                    "category",
                    "",
                ),
                "model_name": model_name,
                "model_revision": model_revision,
                "condition": condition,
                "prompt_version": PROMPT_VERSION,
                "prompt_file": prompt_file_used,
                "question": (
                    questions.get(
                        case_id,
                        {},
                    ).get("question", "")
                ),
                "options": (
                    questions.get(
                        case_id,
                        {},
                    ).get("options", "")
                ),
                "image_id": row.get(
                    "image_id",
                    "",
                ),
                "image_path": image_path,
                "mismatch_source_id": row.get(
                    "mismatch_source_id",
                    "",
                ),
                "gold_answer": row.get(
                    "gold_answer",
                    "",
                ),
                "raw_response": raw_response,
                "generation_parameters": generation_parameters,
                "timestamp": datetime.now().isoformat(),
                "error": error,
            }

            output_file.write(
                json.dumps(
                    output,
                    ensure_ascii=False,
                ) + "\n"
            )
            output_file.flush()

            rows_written += 1
            print(
                f"[{rows_attempted}] "
                f"case_id={case_id} "
                f"condition={condition} "
                f"error={error is not None}"
            )

    elapsed = time.perf_counter() - start_time

    print("")
    print("Run complete.")
    print(f"Rows attempted: {rows_attempted}")
    print(f"Rows written: {rows_written}")
    print(f"Rows failed: {rows_failed}")
    print(f"Time elapsed: {elapsed:.3f} seconds")


if __name__ == "__main__":
    main()
