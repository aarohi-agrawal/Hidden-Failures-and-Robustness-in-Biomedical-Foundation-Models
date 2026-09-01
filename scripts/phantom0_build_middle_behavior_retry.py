import csv
import json
from pathlib import Path

SCORING = Path("annotations/phantom0_middle_scoring_input.csv")
FAILS = Path("annotations/phantom0_middle_judge_parse_failures.csv")
PROMPT = Path("prompts/judges/phantom0_behavior_judge_v1.txt")
OUT = Path("batch_inputs/middle/phantom0_behavior_judge_v1_retry1.jsonl")

MODEL = "gpt-5.6-luna"

rows = {r["row_id"]: r for r in csv.DictReader(open(SCORING, encoding="utf-8-sig"))}
fails = list(csv.DictReader(open(FAILS, encoding="utf-8-sig")))
failed_ids = [r["row_id"] for r in fails]
prompt_template = PROMPT.read_text(encoding="utf-8")

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", encoding="utf-8") as f:
    for row_id in failed_ids:
        row = rows[row_id]
        prompt = prompt_template.replace("{model_answer}", row["raw_response"])
        obj = {
            "custom_id": f"behavior_retry1_{row_id}",
            "method": "POST",
            "url": "/v1/responses",
            "body": {
                "model": MODEL,
                "input": prompt,
                "max_output_tokens": 200,
                "store": False
            }
        }
        f.write(json.dumps(obj) + "\n")

print("wrote", OUT, "rows=", len(failed_ids))
