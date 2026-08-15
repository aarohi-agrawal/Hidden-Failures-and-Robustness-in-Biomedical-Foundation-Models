import csv
import json
import os
from pathlib import Path

MODEL = os.getenv("PHANTOM0_JUDGE_MODEL", "gpt-5.6-luna")

def clean_text(value):
    return " ".join((value or "").split())

def make_request(custom_id, prompt, max_output_tokens):
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/responses",
        "body": {
            "model": MODEL,
            "input": prompt,
            "max_output_tokens": max_output_tokens,
            "store": False
        }
    }

scoring_rows = {r["row_id"]: r for r in csv.DictReader(open("annotations/phantom0_scoring_input.csv", encoding="utf-8-sig"))}
scored_rows = list(csv.DictReader(open("annotations/phantom0_all_scored.csv", encoding="utf-8-sig")))

mirage_template = Path("prompts/judges/phantom0_mirage_judge_v1.txt").read_text(encoding="utf-8")
behavior_template = Path("prompts/judges/phantom0_behavior_judge_v1.txt").read_text(encoding="utf-8")

Path("batch_inputs").mkdir(exist_ok=True)

mirage_retry = []
behavior_retry = []

for row in scored_rows:
    if row.get("judge_parse_success") == "yes":
        continue

    base = scoring_rows[row["row_id"]]
    raw_response = clean_text(base.get("raw_response", ""))

    if row.get("mirage_judge_parse_success") != "yes":
        prompt = mirage_template.replace("{model_answer}", raw_response)
        mirage_retry.append(make_request(f"{row['row_id']}__mirage_v1_retry1", prompt, 200))

    if row.get("behavior_judge_parse_success") != "yes":
        prompt = behavior_template.replace("{model_answer}", raw_response)
        behavior_retry.append(make_request(f"{row['row_id']}__behavior_v1_retry1", prompt, 400))

with open("batch_inputs/phantom0_mirage_judge_v1_retry1.jsonl", "w", encoding="utf-8") as f:
    for r in mirage_retry:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

with open("batch_inputs/phantom0_behavior_judge_v1_retry1.jsonl", "w", encoding="utf-8") as f:
    for r in behavior_retry:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("model", MODEL)
print("mirage retry rows", len(mirage_retry))
print("behavior retry rows", len(behavior_retry))
