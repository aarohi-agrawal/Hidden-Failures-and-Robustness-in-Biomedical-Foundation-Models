import json
from datetime import date
from pathlib import Path

import yaml
from transformers import pipeline

def main():
    # Load config
    with open("configs/week0_vlm_smoke_test.yaml", "r") as f:
        config = yaml.safe_load(f)

    models = [
        "HuggingFaceTB/SmolVLM-256M-Instruct", 
        "Qwen/Qwen2.5-VL-3B-Instruct"
    ]

    # Public image from Hugging Face docs
    image_url = config["image_url"]
    question = config["question"]

    outputs = []

    for i, model_name in enumerate(models):
        try:
            pipe = pipeline(
                "image-to-text",
                model = model_name
            )

            result = pipe(image_url)
            raw_response = str(result)
            run_status = "success"

        except Exception as e:
            raw_response = f"ERROR: {str(e)}"
            run_status = "failed"

        outputs.append({
            "case_id": f"case_{i:03d}_{model_name.split('/')[-1]}",
            "model_name": model_name,
            "prompt_version": config["prompt_version"],
            "condition": config["condition"],
            "question": question,
            "raw_response": raw_response,
            "run_status": run_status,
            "timestamp": str(date.today()),
            "notes": "Multi-model run"
        })

    print(outputs)

    # output_path = Path(config["output_file"])
    # output_path.parent.mkdir(parents=True, exist_ok=True)

    # with open(output_path, "w") as f:
    #     f.write(json.dumps(output) + "\n")

    # print(f"Output written to {output_path}")


if __name__ == "__main__":
    main()
