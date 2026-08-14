import csv
import json
from datetime import date
from transformers import AutoProcessor, AutoModelForImageTextToText

file_path = "data/manifests/mmstar_60case_frozen.csv"
mismatch_path = "data/manifests/mmstar_mismatch_map.csv"
model_name = "HuggingFaceTB/SmolVLM-256M-Instruct"
output_file = open(f"outputs/raw/mmstar_{model_name}.jsonl", "w", encoding="utf-8")

processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(model_name)
bundle_id = 0

image_conditions = {
    "correct_image",
    "no_image",
    "blank_image",
    "far_mismatch",
    "hard_mismatch"
}

mismatch_map = {}

with open(mismatch_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    # Load each row into mismatch map dictionary for easy access
    for row in reader:
        mismatch_map[row["source_id"]] = row

with open(file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        mismatch_source_ids = {
            "far_mismatch": mismatch_map["far_mismatch_source_id"],
            "hard_mismatch": mismatch_map["hard_mismatch_source_id"],
        }

        for condition in image_conditions:
            question = row["question"]
            options = row["options"]

            prompt_version = "mmstar_evidence_integrity_v1"
            prompt_file = f"prompts/{prompt_version}.txt"

            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            prompt = prompt_template.format(question=question, options=options)

            output = {
                "dataset": "mmstar",
                "source_id": row["source_id"],
                "bundle_id": f"bundle_{bundle_id}",
                "model_name": model_name,
                "model_revision": "main",
                "condition": condition,
                "category": row["category"],
                "l2_category": row["l2_category"],
                "question": question,
                "options": options,
                "official_gold": row["answer"],
                "image_path": row["image_path"],
                "mismatch_source_id": mismatch_source_ids["condition"],
                "raw_response": raw_response,
                "prompt_version": prompt_version,
                "temperature": 0.0,
                "max_new_tokens": 128,
                "timestamp": str(date.today()),
                "error": error
            }

            output_file.write(json.dumps(output) + "\n")
           
    output_file.close()
        


