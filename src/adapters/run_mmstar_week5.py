import csv
import json
from datetime import date
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
import argparse

# Added argparse code to make model name a command line argument
parser = argparse.ArgumentParser()
parser.add_argument(
    "--model",
    required=True,
    help="Enter model name"
)
args = parser.parse_args()

file_path = "data/manifests/mmstar_60case_frozen.csv"
mismatch_path = "data/manifests/mmstar_mismatch_map.csv"
model_name = args.model

formatted_name = model_name.split("/")[-1]
output_file = open(f"outputs/raw/mmstar_{formatted_name}.jsonl", "w", encoding="utf-8")

processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(model_name)
bundle_id = 0

image_conditions = [
    "correct_image",
    "no_image",
    "blank_image",
    "far_mismatch",
    "hard_mismatch"
]

mismatch_map = {}

with open(mismatch_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    # Load each row into mismatch map dictionary for easy access
    for row in reader:
        mismatch_map[row["source_id"]] = row

with open(file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        mismatch = mismatch_map[row["source_id"]]

        mismatch_source_ids = {
            "far_mismatch": mismatch["far_mismatch_source_id"],
            "hard_mismatch": mismatch["hard_mismatch_source_id"],
        }

        image_paths = {
            "correct_image": row["image_path"],
            "no_image": "",
            "blank_image": "data/generated/blank_image_white.png",
            "far_mismatch": mismatch["far_mismatch_image_path"],
            "hard_mismatch": mismatch["hard_mismatch_image_path"]
        }

        for condition in image_conditions:
            question = row["question"]
            options = row["options"]

            prompt_version = "mmstar_evidence_integrity_v1"
            prompt_file = f"prompts/{prompt_version}.txt"

            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            prompt = prompt_template.format(question=question, options=options)
            image_path = image_paths[condition]

            try:
                if image_path:
                    image = Image.open(image_path).convert("RGB")
                
                    chat = [
                        {
                            "role": "user",
                            "content":[{"type":"image"}, {"type":"text", "text":prompt}]
                        }
                    ]

                    text = processor.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
                    inputs = processor(text=text, images=[image], return_tensors="pt")
                else:
                    chat = [
                        {
                            "role": "user",
                            "content":[{"type":"text", "text":prompt}]
                        }
                    ]

                    text = processor.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
                    inputs = processor(text=text, return_tensors="pt")

                generated_ids = model.generate(**inputs, max_new_tokens=128)
                generated_ids = generated_ids[:, inputs["input_ids"].shape[1]:]

                error = None
                raw_response = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

            except Exception as e:
                error = str(e)
                raw_response = ""

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
                "mismatch_source_id": mismatch_source_ids.get(condition),
                "raw_response": raw_response,
                "prompt_version": prompt_version,
                "temperature": 0.0,
                "max_new_tokens": 128,
                "timestamp": str(date.today()),
                "error": error
            }

            output_file.write(json.dumps(output) + "\n")
            print(f"{condition} row for bundle_{bundle_id} completed")
        
        bundle_id += 1
           
    output_file.close()
        


