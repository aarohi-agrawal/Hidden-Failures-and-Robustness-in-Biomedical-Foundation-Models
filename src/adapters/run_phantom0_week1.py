import csv
import json
from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
from datetime import date
import time

file_path = "data/manifests/week1_phantom0_eval.csv"
model_name = "HuggingFaceTB/SmolVLM-256M-Instruct"
output_file = open("outputs/raw/week1_phantom0_model1.jsonl", "w", encoding="utf-8")

processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(model_name)

start_time = time.perf_counter()

with open(file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        if row["include_in_eval"].lower() != "no":
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

                generated_ids = model.generate(**inputs, max_new_tokens=128)
                generated_ids = generated_ids[:, inputs["input_ids"].shape[1]:]

                error = None
                raw_response = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

            except Exception as e:
                error = str(e)
                raw_response = ""

            output = {
                "run_id": f"week1_model1_{row['case_id'][-3:]}",
                "case_id": row["case_id"],
                "source_id": row["source_id"],
                "model_name": model_name,
                "evidence_condition": row["evidence_condition"],
                "prompt_condition": row["prompt_condition"],
                "prompt_version": row["prompt_version"],
                "question": row["question"],
                "raw_response": raw_response,
                "temperature": 0.0,
                "max_new_tokens": 128,
                "timestamp": str(date.today()),
                "error": error
            }

            output_file.write(json.dumps(output) + "\n")
           
    output_file.close()

end_time = time.perf_counter()
time_elapsed = end_time - start_time

print(f"Time elapsed: {time_elapsed:.3f} seconds")
        


