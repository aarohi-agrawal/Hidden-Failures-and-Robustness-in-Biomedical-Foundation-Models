import argparse
import csv
import json
import time
from datetime import date
from pathlib import Path

import torch
from transformers import AutoProcessor


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def load_model(model_name: str):
    if "Qwen2.5-VL" in model_name:
        from transformers import Qwen2_5_VLForConditionalGeneration

        return Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
        )

    from transformers import AutoModelForImageTextToText

    return AutoModelForImageTextToText.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto",
    )


def get_prompt(row):
    prompt_version = row.get("prompt_version", "").strip()
    prompt_file = Path("prompts") / f"{prompt_version}.txt"

    if prompt_file.exists():
        with open(prompt_file, "r", encoding="utf-8") as f:
            template = f.read()
        return template.format_map(SafeDict(row)), str(prompt_file)

    return row.get("question", ""), ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="data/manifests/week2_mmvp_eval.csv",
    )
    parser.add_argument(
        "--output",
        default="outputs/raw/week2_mmvp_model1.jsonl",
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen2.5-VL-3B-Instruct",
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
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model_name = args.model

    print(f"Manifest: {manifest_path}")
    print(f"Output: {output_path}")
    print(f"Model: {model_name}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    processor = AutoProcessor.from_pretrained(model_name)
    model = load_model(model_name)

    start_time = time.perf_counter()

    rows_attempted = 0
    rows_written = 0
    rows_failed = 0

    with open(manifest_path, newline="", encoding="utf-8") as file, open(
        output_path, "w", encoding="utf-8"
    ) as output_file:
        reader = csv.DictReader(file)

        for row in reader:
            if args.limit is not None and rows_attempted >= args.limit:
                break

            if row.get("include_in_eval", "").lower() == "no":
                continue

            rows_attempted += 1

            condition = row.get("condition", "").strip()
            image_path = row.get("image_path", "").strip()

            try:
                prompt, prompt_file_used = get_prompt(row)

                uses_image = condition in [
                    "image_present",
                    "blank_image",
                    "mismatched_image",
                ]

                if uses_image:
                    if not image_path:
                        raise FileNotFoundError(
                            f"No image_path provided for condition={condition}"
                        )

                    if not Path(image_path).exists():
                        raise FileNotFoundError(f"Image not found: {image_path}")

                    from qwen_vl_utils import process_vision_info

                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "image", "image": image_path},
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ]

                    text = processor.apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                    )

                    image_inputs, video_inputs = process_vision_info(messages)

                    inputs = processor(
                        text=[text],
                        images=image_inputs,
                        videos=video_inputs,
                        padding=True,
                        return_tensors="pt",
                    )

                else:
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ]

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
                    inputs = inputs.to(model.device)
                except Exception:
                    pass

                with torch.no_grad():
                    generated_ids = model.generate(
                        **inputs,
                        max_new_tokens=args.max_new_tokens,
                    )

                generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]

                raw_response = processor.batch_decode(
                    generated_ids,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=False,
                )[0]

                error = None

            except Exception as e:
                raw_response = ""
                prompt_file_used = ""
                error = str(e)
                rows_failed += 1

            output = {
                "run_id": f"week2_mmvp_model1_{rows_attempted:03d}",
                "case_id": row.get("case_id", ""),
                "bundle_id": row.get("bundle_id", ""),
                "source_id": row.get("source_id", ""),
                "dataset": row.get("dataset", ""),
                "model_name": model_name,
                "condition": row.get("condition", ""),
                "prompt_version": row.get("prompt_version", ""),
                "prompt_file_used": prompt_file_used,
                "question": row.get("question", ""),
                "gold_answer": row.get("gold_answer", ""),
                "image_path": row.get("image_path", ""),
                "mismatched_image_path": row.get("mismatched_image_path", ""),
                "notes": row.get("notes", ""),
                "raw_response": raw_response,
                "temperature": 0.0,
                "max_new_tokens": args.max_new_tokens,
                "timestamp": str(date.today()),
                "error": error,
            }

            output_file.write(json.dumps(output, ensure_ascii=False) + "\n")
            rows_written += 1

            print(
                f"[{rows_attempted}] case_id={row.get('case_id', '')} "
                f"condition={condition} error={error is not None}"
            )

    end_time = time.perf_counter()

    print("")
    print("Run complete.")
    print(f"Rows attempted: {rows_attempted}")
    print(f"Rows written: {rows_written}")
    print(f"Rows failed: {rows_failed}")
    print(f"Time elapsed: {end_time - start_time:.3f} seconds")


if __name__ == "__main__":
    main()