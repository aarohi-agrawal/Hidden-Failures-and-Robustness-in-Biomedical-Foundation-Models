import argparse
import csv
import json
import os
from pathlib import Path


def load_text(path):
    return Path(path).read_text(encoding="utf-8")


def clean_text(value):
    return " ".join((value or "").split())


def make_response_request(custom_id, model, prompt, max_output_tokens):
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/responses",
        "body": {
            "model": model,
            "input": prompt,
            "max_output_tokens": max_output_tokens,
            "store": False
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="annotations/phantom0_scoring_input.csv")
    parser.add_argument("--outdir", default="batch_inputs")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model", default=os.getenv("PHANTOM0_JUDGE_MODEL", "gpt-5-6-luna"))
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    mirage_prompt_template = load_text("prompts/judges/phantom0_mirage_judge_v1.txt")
    behavior_prompt_template = load_text("prompts/judges/phantom0_behavior_judge_v1.txt")

    rows = list(csv.DictReader(open(args.input, encoding="utf-8-sig")))
    if args.limit is not None:
        rows = rows[:args.limit]

    suffix = f"test{args.limit}" if args.limit else "full"
    mirage_path = outdir / f"phantom0_mirage_judge_v1_{suffix}.jsonl"
    behavior_path = outdir / f"phantom0_behavior_judge_v1_{suffix}.jsonl"

    with mirage_path.open("w", encoding="utf-8") as f_mirage, behavior_path.open("w", encoding="utf-8") as f_behavior:
        for row in rows:
            row_id = row["row_id"]
            raw_response = clean_text(row.get("raw_response", ""))

            mirage_prompt = mirage_prompt_template.replace("{model_answer}", raw_response)
            behavior_prompt = behavior_prompt_template.replace("{model_answer}", raw_response)

            f_mirage.write(json.dumps(make_response_request(
                custom_id=f"{row_id}__mirage_v1",
                model=args.model,
                prompt=mirage_prompt,
                max_output_tokens=50
            ), ensure_ascii=False) + "\n")

            f_behavior.write(json.dumps(make_response_request(
                custom_id=f"{row_id}__behavior_v1",
                model=args.model,
                prompt=behavior_prompt,
                max_output_tokens=120
            ), ensure_ascii=False) + "\n")

    print(f"model={args.model}")
    print(f"wrote {mirage_path} rows={len(rows)}")
    print(f"wrote {behavior_path} rows={len(rows)}")


if __name__ == "__main__":
    main()
