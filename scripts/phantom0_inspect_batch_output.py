import argparse
import json
from pathlib import Path


def extract_text(body):
    if not isinstance(body, dict):
        return ""

    if isinstance(body.get("output_text"), str):
        return body["output_text"]

    pieces = []
    for item in body.get("output", []) or []:
        for content in item.get("content", []) or []:
            if isinstance(content, dict):
                if isinstance(content.get("text"), str):
                    pieces.append(content["text"])
                elif isinstance(content.get("output_text"), str):
                    pieces.append(content["output_text"])
    return "\n".join(pieces).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl")
    args = parser.parse_args()

    path = Path(args.jsonl)
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    print("file:", path)
    print("rows:", len(rows))

    for r in rows:
        custom_id = r.get("custom_id")
        error = r.get("error")
        response = r.get("response") or {}
        status_code = response.get("status_code")
        body = response.get("body") or {}
        text = extract_text(body)

        print("\n---")
        print("custom_id:", custom_id)
        print("status_code:", status_code)
        print("error:", error)
        print("text:", text[:500])


if __name__ == "__main__":
    main()
