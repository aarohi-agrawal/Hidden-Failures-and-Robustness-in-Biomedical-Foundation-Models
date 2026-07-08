import argparse
import csv
import json
import time
from datetime import date
from pathlib import Path

import torch
from transformers import AutoProcessor


def load_model(model_name: str):
    """
    Load the Week 2 larger VLM.
    For Qwen2.5-VL, use the Qwen-specific class when available.
    """
    if "Qwen2.5-VL" in model_name:
        from transformers import Qwen2_5_VLForConditionalGeneration

        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
        )
    else:
        from transformers import AutoModelForImageTextToText

        model = AutoModelForImageTextToText.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto",
        )

    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="data/manifests/week2_phantom0_bigger_model_eval.csv",
        help="Input manifest CSV.",
    )
    parser.add_argument(
        "--output",
        default="outputs/raw/week2_phantom0_bigger_model.jsonl",
        help="Output JSONL file.",
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen2.5-VL-3B-Instruct",
        help="Hugging Face model name.",
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
        help="Optional limit for test runs.",
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

    with open(manifest_path, mode="r", newline="", encoding="utf-8") as file, open(
        output_path, "w", encoding="utf-8"
    ) as output_file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader, start=1):
            if args.limit is not None and rows_attempted >= args.limit:
                break

            if row.get("include_in_eval", "").lower() == "no":
                continue

            rows_attempted += 1

            question = row["question"]
            prompt_version = row["prompt_version"]
            prompt_file = Path("prompts") / f"{prompt_version}.txt"

            try:
                with open(prompt_file, "r", encoding="utf-8") as f:
                    prompt_template = f.read()

                prompt = prompt_template.format(question=question)

                chat = [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    }
                ]

                text = processor.apply_chat_template(
                    chat,
                    tokenize=False,
                    add_generation_prompt=True,
                )

                inputs = processor(text=text, return_tensors="pt")

                # Move inputs to the same device as the model.
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
                )[0]

                error = None

            except Exception as e:
                raw_response = ""
                error = str(e)
                rows_failed += 1

            output = {
                "run_id": f"week2_bigger_model_{rows_attempted:03d}",
                "case_id": row["case_id"],
                "source_id": row["source_id"],
                "domain": row.get("domain", ""),
                "category": row.get("category", ""),
                "model_name": model_name,
                "condition": row.get("condition", ""),
                "prompt_condition": row.get("prompt_condition", ""),
                "prompt_version": row.get("prompt_version", ""),
                "question": row.get("question", ""),
                "raw_response": raw_response,
                "temperature": 0.0,
                "max_new_tokens": args.max_new_tokens,
                "timestamp": str(date.today()),
                "error": error,
            }

            output_file.write(json.dumps(output, ensure_ascii=False) + "\n")
            rows_written += 1

            print(
                f"[{rows_attempted}] case_id={row['case_id']} "
                f"prompt_condition={row.get('prompt_condition', '')} "
                f"error={error is not None}"
            )

    end_time = time.perf_counter()
    time_elapsed = end_time - start_time

    print("")
    print("Run complete.")
    print(f"Rows attempted: {rows_attempted}")
    print(f"Rows written: {rows_written}")
    print(f"Rows failed: {rows_failed}")
    print(f"Time elapsed: {time_elapsed:.3f} seconds")


if __name__ == "__main__":
    main()