import argparse
import json
import os
from pathlib import Path
from openai import OpenAI


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_jsonl")
    parser.add_argument("--metadata-name", default="phantom0_judge")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not loaded. Stop.")

    input_path = Path(args.input_jsonl)
    if not input_path.exists():
        raise SystemExit(f"Missing input file: {input_path}")

    client = OpenAI()

    with input_path.open("rb") as f:
        uploaded = client.files.create(
            file=f,
            purpose="batch"
        )

    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/responses",
        completion_window="24h",
        metadata={
            "name": args.metadata_name,
            "input_file": input_path.name
        }
    )

    result = {
        "input_jsonl": str(input_path),
        "uploaded_file_id": uploaded.id,
        "batch_id": batch.id,
        "status": batch.status,
        "metadata_name": args.metadata_name
    }

    outdir = Path("batch_outputs")
    outdir.mkdir(exist_ok=True)
    outpath = outdir / f"{input_path.stem}_batch_info.json"
    outpath.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result, indent=2))
    print(f"saved {outpath}")


if __name__ == "__main__":
    main()
