import argparse
import os
from pathlib import Path
from openai import OpenAI


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_id")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not loaded. Stop.")

    client = OpenAI()
    batch = client.batches.retrieve(args.batch_id)

    print("batch_id:", batch.id)
    print("status:", batch.status)
    print("output_file_id:", batch.output_file_id)
    print("error_file_id:", batch.error_file_id)

    if batch.status != "completed":
        raise SystemExit(f"Batch is not completed yet: {batch.status}")

    if not batch.output_file_id:
        raise SystemExit("No output_file_id found.")

    outpath = Path(args.out)
    outpath.parent.mkdir(parents=True, exist_ok=True)

    content = client.files.content(batch.output_file_id)
    try:
        content.write_to_file(outpath)
    except AttributeError:
        outpath.write_bytes(content.read())

    print(f"downloaded {outpath}")


if __name__ == "__main__":
    main()
