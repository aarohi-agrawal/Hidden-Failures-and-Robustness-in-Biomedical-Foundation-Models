import csv
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch

file_path = "data/manifests/week1_phantom0_eval_test3.csv"
model_name = "HuggingFaceTB/SmolVLM-256M-Instruct"

processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(model_name)

with open(file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        if row.get("include_in_eval", "yes").lower() != "no":
            question = row["question"]

            prompt_version = row["prompt_version"]
            prompt_file = f"prompts/{prompt_version}.txt"

            with open(prompt_file, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            prompt = prompt_template.format(question=row["question"])

            try:
                chat = [
                    {
                        "role": "user",
                        "content":[{"type":"text", "text":prompt}]
                    }
                ]

                text = processor.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=text, return_tensors="pt")
                
            except Exception as e:
                error = str(e)
                raw_response = ""

            

        


