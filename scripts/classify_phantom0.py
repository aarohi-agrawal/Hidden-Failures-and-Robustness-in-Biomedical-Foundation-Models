import pandas as pd
import json
from transformers import pipeline

input_file = "annotations/week4_phantom0_annotation_input.csv"
output_file = "annotations/week4_phantom0_annotation_input.csv"

classifier = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-VL-3B-Instruct"
)

df = pd.read_csv(input_file)

df["auto_response_mode"] = ""
df["auto_evidence_issue_acknowledged"] = ""

prompt_file = "phantom0_classifier.txt"

with open(prompt_file, "r", encoding="utf-8") as f:
    prompt_template = f.read()

for i, row in df.iterrows():
    question = row["question"]
    response = row["raw_response"]

    prompt = prompt_template.format(question=question, raw_response=response)

    result = classifier(prompt, max_new_tokens=100)[0]["generated_text"]

    try:
        labels = json.loads(result)

        df.at[i, "auto_response_mode"] = labels["response_mode"]
        df.at[i, "auto_evidence_issue_acknowledged"] = labels["evidence_issue_acknowledged"]
    
    except Exception as e:
        print(f"Could not classify row {i}: {e}")

df.to_csv(output_file, index=False)



    