import csv
import json
from transformers import AutoProcessor, AutoModelForImageTextToText

file_path = "data/manifests/mmstar_60case_frozen.csv"
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

with open(file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        for condition in image_conditions:
            
            output = {
                "dataset": "mmstar",
                "source_id": row["source_id"]",
                "bundle_id": f"bundle_{bundle_id}",
                "model_name": model_name,
                "model_revision": "main",
                "condition": condition,
                "category": row["category"],
                "l2_category": row["l2_category"],
                "question": row["question"],
                "options": row["options"],
                "official_gold": row["answer"],
                "question": row["question"],
                "raw_response": raw_response,
                "temperature": 0.0,
                "max_new_tokens": 128,
                "timestamp": str(date.today()),
                "error": error
            }

            output_file.write(json.dumps(output) + "\n")
           
    output_file.close()
        


