import json
import csv
from openai import OpenAI

client = OpenAI()

input_files = [
    "outputs/raw/mmstar_Qwen2.5-VL-3B-Instruct.jsonl",
    "outputs/raw/mmstar_Qwen2.5-VL-7B-Instruct.jsonl",
    "outputs/raw/mmstar_SmolVLM-256M-Instruct.jsonl",
]
output_file = open(f"annotation/mmstar_auto_parsed.csv", "a", encoding="utf-8")

judge_model = "gpt-5.6"

def parse_evidence_behavior(raw_response):
    

def parse_answer(question, options, raw_response):
