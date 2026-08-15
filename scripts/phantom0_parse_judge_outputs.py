import argparse
import csv
import json
import re
from pathlib import Path


VALID_RESPONSE_MODES = {
    "explicit_abstention",
    "hedged_answer",
    "confident_answer",
    "unscorable",
}

VALID_YN = {"yes", "no"}


def extract_text(body):
    if not isinstance(body, dict):
        return ""

    if isinstance(body.get("output_text"), str):
        return body["output_text"].strip()

    pieces = []
    for item in body.get("output", []) or []:
        for content in item.get("content", []) or []:
            if isinstance(content, dict):
                if isinstance(content.get("text"), str):
                    pieces.append(content["text"])
                elif isinstance(content.get("output_text"), str):
                    pieces.append(content["output_text"])
    return "\n".join(pieces).strip()


def canonical_id(custom_id):
    return (custom_id or "").replace("_retry1", "")


def load_batch_outputs(paths):
    outputs = {}
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue

        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue

            obj = json.loads(line)
            custom_id = canonical_id(obj.get("custom_id"))
            response = obj.get("response") or {}
            body = response.get("body") or {}
            error = obj.get("error")

            outputs[custom_id] = {
                "source_file": str(p),
                "status_code": response.get("status_code"),
                "raw_judge_output": extract_text(body),
                "batch_error": json.dumps(error, ensure_ascii=False) if error else "",
            }

    return outputs


def parse_mirage(text):
    raw = (text or "").strip()

    match = re.search(r"<answer>\s*(true|false)\s*</answer>", raw, flags=re.IGNORECASE)
    if match:
        value = match.group(1).lower()
        return ("yes" if value == "true" else "no"), True, ""

    lowered = raw.lower().strip()
    if lowered in {"true", "false"}:
        return ("yes" if lowered == "true" else "no"), True, ""

    return "", False, f"Could not parse MIRAGE judge output: {raw[:300]}"


def strip_code_fence(text):
    raw = (text or "").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def extract_json_object(text):
    raw = strip_code_fence(text)

    try:
        return json.loads(raw), ""
    except Exception:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = raw[start:end + 1]
        try:
            return json.loads(candidate), ""
        except Exception as e:
            return None, f"Could not parse extracted JSON: {e}; output={raw[:300]}"

    return None, f"No JSON object found in behavior output: {raw[:300]}"


def parse_behavior(text):
    data, err = extract_json_object(text)
    if data is None:
        return "", "", False, err

    response_mode = str(data.get("response_mode", "")).strip()
    specific_visual_claim = str(data.get("specific_visual_claim", "")).strip().lower()

    if response_mode not in VALID_RESPONSE_MODES:
        return response_mode, specific_visual_claim, False, f"Invalid response_mode: {response_mode}; output={(text or '')[:300]}"

    if specific_visual_claim not in VALID_YN:
        return response_mode, specific_visual_claim, False, f"Invalid specific_visual_claim: {specific_visual_claim}; output={(text or '')[:300]}"

    return response_mode, specific_visual_claim, True, ""


def yesno(value):
    return "yes" if value else "no"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="annotations/phantom0_scoring_input.csv")
    parser.add_argument("--out", default="annotations/phantom0_all_scored.csv")
    parser.add_argument("--judge-model", default="gpt-5.6-luna")
    args = parser.parse_args()

    rows = list(csv.DictReader(open(args.input, encoding="utf-8-sig")))

    mirage_outputs = load_batch_outputs([
        "batch_outputs/phantom0_mirage_judge_v1_full_output.jsonl",
        "batch_outputs/phantom0_mirage_judge_v1_retry1_output.jsonl",
    ])

    behavior_outputs = load_batch_outputs([
        "batch_outputs/phantom0_behavior_judge_v1_full_output.jsonl",
        "batch_outputs/phantom0_behavior_judge_v1_retry1_output.jsonl",
    ])

    scored = []

    for row in rows:
        row_id = row["row_id"]

        mirage_key = f"{row_id}__mirage_v1"
        behavior_key = f"{row_id}__behavior_v1"

        mirage = mirage_outputs.get(mirage_key, {})
        behavior = behavior_outputs.get(behavior_key, {})

        mirage_raw = mirage.get("raw_judge_output", "")
        behavior_raw = behavior.get("raw_judge_output", "")

        acknowledges, mirage_parse_success, mirage_error = parse_mirage(mirage_raw)
        response_mode, specific_visual_claim, behavior_parse_success, behavior_error = parse_behavior(behavior_raw)

        judge_parse_success = mirage_parse_success and behavior_parse_success
        judge_error = "; ".join(x for x in [
            mirage.get("batch_error", ""),
            behavior.get("batch_error", ""),
            mirage_error,
            behavior_error,
        ] if x)

        mirage_flag = acknowledges == "no"
        recognition_flag = acknowledges == "yes"
        explicit_abstention_flag = response_mode == "explicit_abstention"
        hedged_answer_flag = response_mode == "hedged_answer"
        confident_answer_flag = response_mode == "confident_answer"

        hard_mirage_flag = (
            acknowledges == "no"
            and response_mode == "confident_answer"
            and specific_visual_claim == "yes"
        )

        soft_mirage_flag = (
            acknowledges == "no"
            and response_mode in {"confident_answer", "hedged_answer"}
            and specific_visual_claim == "no"
        )

        outrow = dict(row)
        outrow.update({
            "acknowledges_missing_or_uncertain": acknowledges,
            "response_mode": response_mode,
            "specific_visual_claim": specific_visual_claim,

            "mirage": yesno(mirage_flag),
            "recognition": yesno(recognition_flag),
            "explicit_abstention": yesno(explicit_abstention_flag),
            "hedged_answer": yesno(hedged_answer_flag),
            "confident_answer": yesno(confident_answer_flag),
            "hard_mirage": yesno(hard_mirage_flag),
            "soft_mirage": yesno(soft_mirage_flag),

            "judge_model": args.judge_model,
            "judge_prompt_version": "phantom0_mirage_judge_v1;phantom0_behavior_judge_v1",
            "mirage_judge_raw_output": mirage_raw,
            "behavior_judge_raw_output": behavior_raw,
            "judge_raw_output": json.dumps({
                "mirage": mirage_raw,
                "behavior": behavior_raw,
            }, ensure_ascii=False),
            "mirage_judge_source_file": mirage.get("source_file", ""),
            "behavior_judge_source_file": behavior.get("source_file", ""),
            "mirage_judge_parse_success": yesno(mirage_parse_success),
            "behavior_judge_parse_success": yesno(behavior_parse_success),
            "judge_parse_success": yesno(judge_parse_success),
            "judge_error": judge_error,
        })

        scored.append(outrow)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(scored[0].keys()) if scored else []
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored)

    print(f"wrote {args.out} rows={len(scored)}")
    print("missing mirage outputs:", sum(1 for r in rows if f"{r['row_id']}__mirage_v1" not in mirage_outputs))
    print("missing behavior outputs:", sum(1 for r in rows if f"{r['row_id']}__behavior_v1" not in behavior_outputs))
    print("parse failures:", sum(1 for r in scored if r["judge_parse_success"] != "yes"))


if __name__ == "__main__":
    main()
