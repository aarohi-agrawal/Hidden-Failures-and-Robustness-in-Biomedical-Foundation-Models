import pandas as pd
import json
import re
from transformers import pipeline

input_file = "annotations/week4_phantom0_manual_audit.csv"
output_file = "annotations/week4_phantom0_manual_audit.csv"

classifier = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-VL-3B-Instruct"
)

df = pd.read_csv(input_file)

df["auto_response_mode"] = ""
df["auto_evidence_issue_acknowledged"] = ""

prompt_file = "prompts/phantom0_classifier.txt"

with open(prompt_file, "r", encoding="utf-8") as f:
    prompt_template = f.read()

for i, row in df.head(5).iterrows():
    question = row["question"]
    response = row["raw_response"]

    prompt = prompt_template.format(question=question, raw_response=response)

    result = classifier(prompt, max_new_tokens=100, do_sample = False, return_full_text=False)[0]["generated_text"]
    match = re.search(r'\{.*\}', result, re.DOTALL)

    if match:
        labels = json.loads(match.group())

        df.at[i, "auto_response_mode"] = labels["response_mode"]
        df.at[i, "auto_evidence_issue_acknowledged"] = labels["evidence_issue_acknowledged"]
    
    else:
        print(f"Could not classify row {i}, invalid JSON")
        
    print(f"Processed {i + 1} / {len(df)}")

df.to_csv(output_file, index=False)



    