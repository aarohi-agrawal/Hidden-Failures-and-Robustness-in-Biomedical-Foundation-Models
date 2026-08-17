from openai import OPENAI

input_files = [
    "outputs/raw/mmstar_Qwen2.5-VL-3B-Instruct.jsonl",
    "outputs/raw/mmstar_Qwen2.5-VL-7B-Instruct.jsonl",
    "outputs/raw/mmstar_SmolVLM-256M-Instruct.jsonl",
]

output_file = open(f"annotation/mmstar_auto_parsed.csv", "w", encoding="utf-8")
