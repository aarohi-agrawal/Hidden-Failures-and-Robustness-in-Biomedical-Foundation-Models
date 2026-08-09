import pandas as pd
import json
import re
from transformers import pipeline

input_file = "annotations/week4/phantom0_annotation_input.csv"
output_file = "annotations/week4/phantom0_annotation_input.csv"

classifier = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-VL-3B-Instruct"
)

df = pd.read_csv(input_file)

df["auto_response_mode"] = ""
df["auto_evidence_issue_acknowledged"] = ""

for i, row in df.iterrows():
    question = row["question"]
    response = row["raw_response"]

    prompt_file = "phantom0_classifier.txt"

    with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_template = f.read()
            prompt = prompt_template.format(question=question, raw_response=response)

    

    