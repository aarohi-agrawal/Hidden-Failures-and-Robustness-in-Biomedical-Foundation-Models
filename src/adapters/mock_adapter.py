import json
from datetime import date

output = {
    "case_id": "week0_mock_001",
    "model_name": "mock_model",
    "prompt_version": "week0_mock_v0",
    "condition": "no_image",
    "question": "What abnormality is shown in the image?",
    "raw_response": "I cannot answer because no image was provided.",
    "timestamp": str(date.today()),
    "notes": "Fallback mock output because real VLM did not run"
}

with open("outputs/raw/week0_mock_outputs.jsonl", "w") as f:
    f.write(json.dumps(output) + "\n")

print("Mock output written.")
