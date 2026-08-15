import argparse
import os
from openai import OpenAI


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_id")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not loaded. Stop.")

    client = OpenAI()
    batch = client.batches.retrieve(args.batch_id)

    print("batch_id:", batch.id)
    print("status:", batch.status)
    print("request_counts:", batch.request_counts)
    print("output_file_id:", batch.output_file_id)
    print("error_file_id:", batch.error_file_id)
    if batch.errors:
        print("errors:", batch.errors)


if __name__ == "__main__":
    main()
