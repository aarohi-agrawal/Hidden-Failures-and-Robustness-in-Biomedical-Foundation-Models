import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path

import torch
from transformers import AutoProcessor


PROMPT_VERSION = "mmvp_evidence_integrity_v1"


def load_model(model_name: str, model_revision: str = "main"):
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

    with open(prompt_file, "r", encoding="utf-8") as f:
        template = f.read()

    return template.format(question=question), str(prompt_file)


def build_messages(condition, prompt, image_path):
    image_conditions = {
        "image_present",
        "blank_image",
        "mismatched_image",
    }

    if condition in image_conditions:
        if not image_path:
            raise FileNotFoundError(
                f"No image_path provided for condition={condition}"
            )

        if not Path(image_path).exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        messages = [
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

        return messages

    if condition == "no_image":
        messages = [
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

        return messages

    raise ValueError(
        f"Unknown condition: {condition}"
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to the 64-row Week 3 MMVP manifest.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output JSONL file.",
    )

    parser.add_argument(
        "--model",
        required=True,
        help="Model identifier.",
    )

    parser.add_argument(
        "--model-revision",
        default="main",
        help="Model revision or commit identifier.",
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
        help="Optional number of rows to run for validation.",
    )

    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    output_path = Path(args.output)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_name = args.model
    model_revision = args.model_revision

    generation_parameters = {
        "temperature": 0.0,
        "do_sample": False,
        "max_new_tokens": args.max_new_tokens,
    }

    print(f"Manifest: {manifest_path}")
    print(f"Output: {output_path}")
    print(f"Model: {model_name}")
    print(f"Model revision: {model_revision}")
    print(f"Prompt version: {PROMPT_VERSION}")
    print(f"Generation parameters: {generation_parameters}")
    print(f"CUDA available: {torch.cuda.is_available()}")

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
    ) as file, open(
        output_path,
        "w",
        encoding="utf-8",
    ) as output_file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                args.limit is not None
                and rows_attempted >= args.limit
            ):
                break

            if (
                row.get("include_in_eval", "")
                .lower()
                == "no"
            ):
                continue

            rows_attempted += 1

            condition = row.get(
                "condition",
                "",
            ).strip()

            image_path = row.get(
                "image_path",
                "",
            ).strip()

            question = row.get(
                "question",
                "",
            ).strip()

            raw_response = ""
            error = None
            prompt_file_used = ""

            try:
                # Use the exact same prompt template
                # for every evidence condition.
                prompt, prompt_file_used = load_prompt(
                    question
                )

                messages = build_messages(
                    condition,
                    prompt,
                    image_path,
                )

                from qwen_vl_utils import (
                    process_vision_info
                )

                uses_image = condition in {
                    "image_present",
                    "blank_image",
                    "mismatched_image",
                }

                if uses_image:

                    text = processor.apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                    )

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

                    text = processor.apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                    )

                    inputs = processor(
                        text=[text],
                        padding=True,
                        return_tensors="pt",
                    )

                try:
                    inputs = inputs.to(
                        model.device
                    )
                except Exception:
                    pass

                with torch.no_grad():

                    generated_ids = model.generate(
                        **inputs,
                        max_new_tokens=(
                            args.max_new_tokens
                        ),
                        do_sample=False,
                        temperature=0.0,
                    )

                generated_ids = (
                    generated_ids[
                        :,
                        inputs[
                            "input_ids"
                        ].shape[1]:,
                    ]
                )

                raw_response = (
                    processor.batch_decode(
                        generated_ids,
                        skip_special_tokens=True,
                        clean_up_tokenization_spaces=False,
                    )[0]
                )

            except Exception as e:

                raw_response = ""
                error = str(e)
                rows_failed += 1

            output = {
                "run_id": (
                    f"week3_{model_name.split('/')[-1]}"
                    f"_{rows_attempted:03d}"
                ),
                "case_id": row.get(
                    "case_id",
                    "",
                ),
                "bundle_id": row.get(
                    "bundle_id",
                    "",
                ),
                "source_id": row.get(
                    "source_id",
                    "",
                ),
                "model_name": model_name,
                "model_revision": model_revision,
                "dataset": row.get(
                    "dataset",
                    "",
                ),
                "condition": row.get(
                    "condition",
                    "",
                ),
                "prompt_version": PROMPT_VERSION,
                "question": question,
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
                "generation_parameters": (
                    generation_parameters
                ),
                "timestamp": (
                    datetime.now().isoformat()
                ),
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
                f"case_id="
                f"{row.get('case_id', '')} "
                f"condition={condition} "
                f"error={error is not None}"
            )

    end_time = time.perf_counter()

    print("")
    print("Run complete.")
    print(
        f"Rows attempted: "
        f"{rows_attempted}"
    )
    print(
        f"Rows written: "
        f"{rows_written}"
    )
    print(
        f"Rows failed: "
        f"{rows_failed}"
    )
    print(
        f"Time elapsed: "
        f"{end_time - start_time:.3f} seconds"
    )


if __name__ == "__main__":
    main()
