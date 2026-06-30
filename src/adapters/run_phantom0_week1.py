import csv

file_path = r"data/manifests/week1_phantom0_eval.csv"

with open(file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)

for row in reader:
    if row["include_in_eval"].lower() != "no":
        question = row["question"]

        prompt_version = row["prompt_version"]
        prompt_file = f"prompts/{prompt_version}.txt"

        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        prompt = prompt_template.format(question=row["question"])
        