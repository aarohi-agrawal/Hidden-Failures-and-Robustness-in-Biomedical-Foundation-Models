import json
import csv
from openai import OpenAI

client = OpenAI()

input_files = [
    "outputs/raw/mmstar_Qwen2.5-VL-3B-Instruct.jsonl",
    "outputs/raw/mmstar_Qwen2.5-VL-7B-Instruct.jsonl",
    "outputs/raw/mmstar_SmolVLM-256M-Instruct.jsonl",
]
output_file = open(f"annotation/mmstar_auto_parsed.csv", "w", encoding="utf-8")

judge_model = "gpt-5.6"

def parse_evidence_behavior(raw_response):
    prompt_file = f"prompts/judges/mmstar_evidence_behavior_judge_v1.txt"

    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(model_answer=raw_response)
    response = client.responses.create(model=judge_model, input=prompt)

    return response.output_text.strip()

def parse_answer(question, options, raw_response):
    prompt_file = f"prompts/judges/mmstar_answer_parser_v1.txt"

    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(question=question, options=options, model_answer=raw_response)
    response = client.responses.create(model=judge_model, input=prompt)

    return response.output_text.strip()

for input_file in input_files:
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)

            question = row["question"]
            options = row["options"]
            raw_response = row["raw_response"]

            evidence_behavior = json.loads(parse_evidence_behavior(raw_response))
            final_answer = parse_answer(question, options, raw_response)

            response_mode = evidence_behavior["response_mode"]
            evidence_issue_acknowledged = evidence_behavior["evidence_issue_acknowledged"]
            specific_visual_claim = evidence_behavior["specific_visual_claim"]

            