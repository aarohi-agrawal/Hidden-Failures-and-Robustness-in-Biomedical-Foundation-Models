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


def load_prompt(question: str):
    prompt_file = Path("prompts") / f"{PROMPT_VERSION}.txt"

    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}"
        )

    template = prompt_file.read_text(encoding="utf-8")
    return template.format(question=question), str(prompt_file)


def resolve_image_path(row):
    condition = row["condition"].strip()
    image_id = row.get("image_id", "").strip()

    if condition == "correct_image":
        return f"data/mmvp/MMVP Images/{image_id}.jpg"

    if condition == "blank_image":
        return f"data/generated/week5_blank_images/{image_id}"

    if condition in {"far_mismatch", "hard_mismatch"}:
        return f"data/mmvp/MMVP Images/{image_id}.jpg"

    if condition == "no_image":
        return ""

    raise ValueError(f"Unknown condition: {condition}")


def validate_manifest_row(row):
    condition = row.get("condition", "").strip()

    allowed = IMAGE_CONDITIONS | {"no_image"}

    if condition not in allowed:
        raise ValueError(
            f"Unknown condition: {condition}"
        )

    question = row.get("question", "").strip()

    if not question:
        raise ValueError(
            f"Missing question for case_id={row.get('case_id')}"
        )

    gold_answer = row.get("gold_answer", "").strip()

    if not gold_answer:
        raise ValueError(
            f"Missing gold_answer for case_id={row.get('case_id')}"
        )

    image_path = resolve_image_path(row)

    if condition == "no_image":
        if image_path:
            raise ValueError(
                "no_image must not have an image path"
            )
    else:
        if not image_path:
            raise ValueError(
                f"Missing image path for {condition}"
            )

        if not Path(image_path).exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

    return image_path


def build_messages(condition, prompt, image_path):
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
                    }
                ],
            }
        ]

    raise ValueError(f"Unknown condition: {condition}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--manifest",
        required=True,
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

    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    output_path = Path(args.output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    generation_parameters = {
        "temperature": 0.0,
        "do_sample": False,
        "max_new_tokens": args.max_new_tokens,
    }

    print(f"Manifest: {manifest_path}")
    print(f"Output: {output_path}")
    print(f"Model: {args.model}")
    print(f"Model revision: {args.model_revision}")
    print(f"Prompt version: {PROMPT_VERSION}")
    print(f"Generation parameters: {generation_parameters}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    processor = AutoProcessor.from_pretrained(
        args.model,
        revision=args.model_revision,
    )

    model = load_model(
        args.model,
        args.model_revision,
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
        "w",
        encoding="utf-8",
    ) as output_file:

        reader = csv.DictReader(manifest_file)

        for row in reader:

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

            raw_response = ""
            error = None
            prompt_file_used = ""
            image_path = ""

            try:
                image_path = validate_manifest_row(row)

                question = row["question"].strip()

                prompt, prompt_file_used = load_prompt(
                    question
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
                    from qwen_vl_utils import process_vision_info

                    image_inputs, video_inputs = (
                        process_vision_info(messages)
                    )

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
                error = str(exception)
                rows_failed += 1

            output = {
                "run_id": (
                    f"week5_"
                    f"{args.model.split('/')[-1]}_"
                    f"{rows_attempted:03d}"
                ),
                "case_id": row.get("case_id", ""),
                "category": row.get("category", ""),
                "model_name": args.model,
                "model_revision": args.model_revision,
                "condition": condition,
                "prompt_version": PROMPT_VERSION,
                "prompt_file": prompt_file_used,
                "question": row.get("question", ""),
                "options": row.get("options", ""),
                "image_id": row.get("image_id", ""),
                "image_path": image_path,
                "mismatch_source_id": row.get(
                    "mismatch_source_id",
                    "",
                ),
                "difficulty_rating": row.get(
                    "difficulty_rating",
                    "",
                ),
                "gold_answer": row.get(
                    "gold_answer",
                    "",
                ),
                "official_question_answer": row.get(
                    "official_question_answer",
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
                )
                + "\n"
            )

            rows_written += 1

            print(
                f"[{rows_attempted}] "
                f"case_id={row.get('case_id', '')} "
                f"condition={condition} "
                f"error={error is not None}"
            )

    elapsed = time.perf_counter() - start_time

    print()
    print("Run complete.")
    print(f"Rows attempted: {rows_attempted}")
    print(f"Rows written: {rows_written}")
    print(f"Rows failed: {rows_failed}")
    print(f"Time elapsed: {elapsed:.3f} seconds")


if __name__ == "__main__":
    main()
