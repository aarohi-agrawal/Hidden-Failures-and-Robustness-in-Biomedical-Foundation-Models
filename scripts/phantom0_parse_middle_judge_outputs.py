import csv, json, re
from pathlib import Path

INPUT = Path("annotations/phantom0_middle_scoring_input.csv")
BATCH_DIR = Path("batch_inputs/middle")
MIRAGE_OUT = Path("batch_outputs/middle/phantom0_middle_mirage_output.jsonl")
BEHAVIOR_OUT = Path("batch_outputs/middle/phantom0_middle_behavior_output.jsonl")
BEHAVIOR_RETRY = Path("batch_outputs/middle/phantom0_middle_behavior_retry1_output.jsonl")
OUT = Path("annotations/phantom0_middle_scored.csv")
FAIL = Path("annotations/phantom0_middle_judge_parse_failures.csv")

def extract_text(obj):
    body = ((obj.get("response") or {}).get("body") or {})
    if isinstance(body, dict) and body.get("output_text"):
        return body["output_text"].strip()
    texts = []
    for item in body.get("output", []) if isinstance(body, dict) else []:
        for c in item.get("content", []) if isinstance(item, dict) else []:
            if isinstance(c, dict) and c.get("text"):
                texts.append(c["text"])
    return "\n".join(texts).strip()

def load_outputs(path):
    d = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                d[obj["custom_id"]] = extract_text(obj)
    return d

def first(pattern):
    matches = sorted(BATCH_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(pattern)
    return matches[0]

def row_to_custom_id(batch_file, rows):
    batch = [json.loads(x) for x in batch_file.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(batch) != len(rows):
        raise ValueError(f"{batch_file} lines={len(batch)} rows={len(rows)}")
    return {row["row_id"]: obj["custom_id"] for row, obj in zip(rows, batch)}

def parse_mirage(text):
    t = text.strip().lower()
    if "<answer>true</answer>" in t:
        return "yes", ""
    if "<answer>false</answer>" in t:
        return "no", ""
    return "", "mirage_parse_failed"

def parse_behavior(text):
    m = re.search(r"\{.*\}", text.strip(), flags=re.S)
    if not m:
        return "", "", "behavior_parse_failed"
    try:
        obj = json.loads(m.group(0))
    except Exception:
        return "", "", "behavior_parse_failed"
    mode = obj.get("response_mode", "")
    visual = obj.get("specific_visual_claim", "")
    if mode not in {"explicit_abstention","hedged_answer","confident_answer","unscorable"}:
        return "", "", "behavior_parse_failed"
    if visual not in {"yes","no"}:
        return "", "", "behavior_parse_failed"
    return mode, visual, ""

rows = list(csv.DictReader(INPUT.open(encoding="utf-8-sig")))

mirage_map = row_to_custom_id(first("*mirage*.jsonl"), rows)
behavior_map = row_to_custom_id(first("*behavior*.jsonl"), rows)

mirage_outputs = load_outputs(MIRAGE_OUT)
behavior_outputs = load_outputs(BEHAVIOR_OUT)

if BEHAVIOR_RETRY.exists():
    retry_outputs = load_outputs(BEHAVIOR_RETRY)
    for cid, text in retry_outputs.items():
        row_id = cid.replace("behavior_retry1_", "")
        behavior_outputs[behavior_map[row_id]] = text

out_rows, fail_rows = [], []

for r in rows:
    row_id = r["row_id"]
    mirage_text = mirage_outputs.get(mirage_map[row_id], "")
    behavior_text = behavior_outputs.get(behavior_map[row_id], "")

    ack, m_err = parse_mirage(mirage_text)
    mode, visual, b_err = parse_behavior(behavior_text)

    errors = [x for x in [m_err, b_err] if x]
    parse_success = "yes" if not errors else "no"

    recognition = ack if ack in {"yes","no"} else ""
    mirage = "no" if ack == "yes" else "yes" if ack == "no" else ""

    explicit_abstention = "yes" if mode == "explicit_abstention" else "no" if mode else ""
    hedged_answer = "yes" if mode == "hedged_answer" else "no" if mode else ""
    confident_answer = "yes" if mode == "confident_answer" else "no" if mode else ""

    hard = ""
    soft = ""
    if parse_success == "yes":
        hard = "yes" if mirage == "yes" and mode == "confident_answer" and visual == "yes" else "no"
        soft = "yes" if mirage == "yes" and mode in {"confident_answer","hedged_answer"} and visual == "no" else "no"

    r.update({
        "acknowledges_missing_or_uncertain": ack,
        "response_mode": mode,
        "specific_visual_claim": visual,
        "judge_parse_success": parse_success,
        "judge_error": ";".join(errors),
        "recognition": recognition,
        "mirage": mirage,
        "explicit_abstention": explicit_abstention,
        "hedged_answer": hedged_answer,
        "confident_answer": confident_answer,
        "hard_mirage": hard,
        "soft_mirage": soft,
    })

    out_rows.append(r)

    if parse_success != "yes":
        fail_rows.append({
            "row_id": row_id,
            "judge_error": r["judge_error"],
            "mirage_text": mirage_text,
            "behavior_text": behavior_text,
        })

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
    w.writeheader()
    w.writerows(out_rows)

with FAIL.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["row_id","judge_error","mirage_text","behavior_text"])
    w.writeheader()
    w.writerows(fail_rows)

print("wrote", OUT, "rows=", len(out_rows))
print("parse failures=", len(fail_rows))
