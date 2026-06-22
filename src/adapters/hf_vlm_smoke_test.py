```python
import json
from datetime import date
from pathlib import Path

import yaml
from transformers import pipeline


def main():
    # Load config
    with open("configs/week0_vlm_smoke_test.yaml", "r") as f:
        config = yaml.safe_load(f)

    model_name = config["model_name"]

    # Public image from Hugging Face docs
    image_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/car.jpg"

    question = "Describe this image in one sentence."

    try:
        pipe = pipeline(
            "image-to-text",
            model=model_name
        )

        result = pipe(image_url)

        raw_response = str(result)

    except Exception as e:
        raw_response = f"ERROR: {str(e)}"

    output = {
        "case_id": "week0_smoke_test_001",
        "model_name": model_name,
        "prompt_version": config["prompt_version"],
        "condition": config["condition"],
        "question": question,
        "raw_response": raw_response,
        "timestamp": str(date.today()),
        "notes": "Week 0 Hugging Face VLM smoke test"
    }

    output_path = Path(config["output_file"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(json.dumps(output) + "\n")

    print(f"Output written to {output_path}")


if __name__ == "__main__":
    main()
```
