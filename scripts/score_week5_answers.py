import json
import re
import argparse
from collections import Counter, defaultdict
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

INPUT = args.input
OUTPUT = args.output

def normalize(s):
    s = str(s or "").lower().strip()
    s = s.replace("\n", " ")
    s = re.sub(r"\s+", " ", s)
    return s


def parse_options(options):
    """
    Extract the two option texts from strings like:
      (a) Yes (b) No
      (a) Dark (b) Light
      (a) 1 (b) 2
    """
    s = normalize(options)

    m = re.search(r"\(a\)\s*(.*?)\s*\(b\)\s*(.*)", s)
    if not m:
        return None, None

    return m.group(1).strip(), m.group(2).strip()


def clean_option_text(x):
    x = normalize(x)
    x = re.sub(r"[^a-z0-9\s\-]", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def answer_from_explicit_letter(text):
    """
    Only accept explicit answer labels when they are reasonably
    unambiguous.
    """
    t = normalize(text)

    patterns_a = [
        r"^\s*\(a\)\s*$",
        r"^\s*answer\s*[:\-]?\s*\(a\)",
        r"^\s*option\s*[:\-]?\s*\(a\)",
        r"^\s*the answer is\s*\(a\)",
    ]

    patterns_b = [
        r"^\s*\(b\)\s*$",
        r"^\s*answer\s*[:\-]?\s*\(b\)",
        r"^\s*option\s*[:\-]?\s*\(b\)",
        r"^\s*the answer is\s*\(b\)",
    ]

    for p in patterns_a:
        if re.search(p, t):
            return "a"

    for p in patterns_b:
        if re.search(p, t):
            return "b"

    return None


def answer_tail(response):
    """
    Models often put the actual answer near the end of a long
    reasoning response. Use the final portion preferentially.
    """
    text = normalize(response)
    return text[-500:]

def semantic_option_match(response, a, b):
    """
    Conservative option-aware semantic matching.

    Returns:
        "a" / "b" / "?"
    """
    r = normalize(response)
    tail = answer_tail(response)

    a_clean = clean_option_text(a)
    b_clean = clean_option_text(b)

    # ------------------------------------------------------------
    # 1. Exact option phrase in the answer tail
    # ------------------------------------------------------------
    for label, opt in [("a", a_clean), ("b", b_clean)]:
        if opt and opt in tail:
            return label

    # ------------------------------------------------------------
    # 1b. Short-form answers / partial option phrases
    # ------------------------------------------------------------

    # Common short forms that correspond to longer options.
    short_forms = {
        "looking down from above": ["above", "down from above"],
        "looking up from below": ["below", "up from below"],

        "all are uncut": [
            "all the fruits are uncut",
            "all fruits are uncut",
            "all are uncut",
        ],

        "some are cut open": [
            "some fruits are cut open",
            "some fruit are cut open",
        ],

        "one": ["1", "one", "single"],
        "more than one": [
            "more than one",
            "multiple",
            "several",
        ],
    }

    for label, opt in [("a", a_clean), ("b", b_clean)]:
        forms = short_forms.get(opt, [])

        for form in forms:
            if re.search(
                rf"(?<!\w){re.escape(form)}(?!\w)",
                tail,
            ):
                return label
    # ------------------------------------------------------------
    # 2. Yes / No
    # ------------------------------------------------------------
    if {a_clean, b_clean} == {"yes", "no"}:
        # Affirmative statements that imply "Yes" even when
        # the response does not literally contain the word "yes".
        affirmative_patterns = [
            r"\bis visible\b",
            r"\bis present\b",
            r"\bis using\b",
            r"\bis holding\b",
            r"\bis wearing\b",
            r"\bis floating\b",
            r"\bis open\b",
            r"\bis facing\b",
            r"\bthere is\b",
            r"\bthere are\b",
            r"\bthe .* is\b",
            r"\bthe .* are\b",
        ]

        for pattern in affirmative_patterns:
            if re.search(pattern, tail):
                return "a" if a_clean == "yes" else "b"
        # Prefer the final sentence / tail.
        yes = bool(re.search(r"\byes\b", tail))
        no = bool(re.search(r"\bno\b", tail))

        if yes and not no:
            return "a" if a_clean == "yes" else "b"

        if no and not yes:
            return "a" if a_clean == "no" else "b"

        # "not visible", "not present", etc.
        if re.search(
            r"\b(?:not|does not|doesn't|isn't|is not|are not|aren't)\b",
            tail,
        ):
            return "a" if a_clean == "no" else "b"

        return "?"

    # ------------------------------------------------------------
    # 3. Correct / Incorrect
    # ------------------------------------------------------------
    if {a_clean, b_clean} == {"correct", "incorrect"}:
        if re.search(r"\bincorrect\b", tail):
            return "a" if a_clean == "incorrect" else "b"

        if re.search(r"\bcorrect\b", tail):
            return "a" if a_clean == "correct" else "b"

        # For questions such as:
        # "Is the following statement correct?"
        # a standalone "No." means the statement is incorrect.
        if re.fullmatch(r"no[\s.!]*", tail):
            return "a" if a_clean == "incorrect" else "b"

        return "?"

    # ------------------------------------------------------------
    # 4. Numeric options
    # ------------------------------------------------------------
    number_map = {
        "0": ["0", "zero", "none", "no"],
        "1": ["1", "one", "single"],
        "2": ["2", "two", "double"],
        "3": ["3", "three"],
        "4": ["4", "four"],
    }

    numeric_options = {}

    for label, opt in [("a", a_clean), ("b", b_clean)]:
        if opt in number_map:
            numeric_options[label] = opt

    if numeric_options:
        hits = []

        for label, number in numeric_options.items():
            for form in number_map[number]:
                if re.search(
                    rf"(?<!\w){re.escape(form)}(?!\w)",
                    tail,
                ):
                    hits.append(label)
                    break

        if len(set(hits)) == 1:
            return hits[0]

        return "?"

    # ------------------------------------------------------------
    # 5. Controlled semantic synonyms
    # ------------------------------------------------------------
    synonym_groups = {
        "yes": ["yes", "true"],
        "no": ["no", "false"],

        "dark": ["dark"],
        "light": ["light"],

        "dark blue": ["dark blue"],
        "light blue": ["light blue"],

        "white": ["white"],
        "black": ["black"],
        "silver": ["silver"],

        "left": ["left", "left side"],
        "right": ["right", "right side"],

        "inward": ["inward", "inwards"],
        "outward": ["outward", "outwards"],

        "upwards": [
            "upwards",
            "upward",
            "above",
            "looking down from above",
            "down from above",
        ],

        "forward": [
            "forward",
            "forwards",
        ],

        "facing forward": [
            "facing forward",
            "forward",
        ],

        "in profile": [
            "in profile",
            "profile",
        ],

        "back view": [
            "back view",
            "from behind",
            "back",
        ],

        "side view": [
            "side view",
            "from the side",
            "side",
        ],

        "floor": [
            "floor",
            "on the floor",
        ],

        "carpet": [
            "carpet",
            "rug",
            "on the rug",
        ],

        "soil": [
            "soil",
            "dirt",
            "on the soil",
        ],

        "palm": [
            "palm",
            "on the palm",
        ],

        "fingers": [
            "fingers",
            "finger",
            "held by the fingers",
        ],

        "slice": [
            "slice",
            "slice of cake",
        ],

        "whole": [
            "whole",
            "whole cake",
        ],

        "shirt": [
            "shirt",
        ],

        "t-shirt": [
            "t-shirt",
            "tshirt",
            "tee shirt",
        ],

        "fillet": [
            "fillet",
            "salmon fillet",
        ],

        "steak": [
            "steak",
            "salmon steak",
        ],

        "more than one": [
            "more than one",
            "multiple",
            "several",
            "variety of trees",
        ],

        "beside the bedside table": [
            "beside the bedside table",
            "beside the bedside",
            "next to the bedside table",
        ],

        "on the windowsill": [
            "on the windowsill",
            "windowsill",
        ],
    }

    def variants(opt):
        if opt in synonym_groups:
            return synonym_groups[opt]
        return [opt]

    scores = {"a": 0, "b": 0}

    for label, opt in [("a", a_clean), ("b", b_clean)]:
        for phrase in variants(opt):
            phrase = clean_option_text(phrase)

            if not phrase:
                continue

            if phrase in tail:
                scores[label] = max(
                    scores[label],
                    len(phrase.split()),
                )

    # Exactly one option supported.
    if scores["a"] > 0 and scores["b"] == 0:
        return "a"

    if scores["b"] > 0 and scores["a"] == 0:
        return "b"

    # Both options appear → don't guess.
    return "?"


def parse_answer(row):
    response = row.get("raw_response", "") or ""
    a, b = parse_options(row.get("options", ""))

    if not a or not b:
        return "?", "invalid_options"

    explicit = answer_from_explicit_letter(response)

    if explicit:
        return explicit, "explicit_letter"

    answer = semantic_option_match(response, a, b)

    if answer != "?":
        return answer, "semantic_match"

    return "?", "unresolved"

def main():
    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)

    rows = []
    with open(INPUT) as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    scored = []

    for row in rows:
        answer, method = parse_answer(row)

        gold = normalize(row.get("gold_answer", ""))
        gold = gold.strip("() ")

        scored_row = dict(row)
        scored_row["parsed_answer"] = answer
        scored_row["parse_method"] = method
        scored_row["correct"] = (
            answer != "?" and answer == gold
        )
        scored.append(scored_row)

    with open(OUTPUT, "w") as f:
        for row in scored:
            f.write(json.dumps(row) + "\n")

    print("Rows:", len(scored))
    print("Parsed:", Counter(r["parsed_answer"] for r in scored))
    print("Methods:", Counter(r["parse_method"] for r in scored))
    print()

    by_condition = defaultdict(list)
    for r in scored:
        by_condition[r["condition"]].append(r)

    for condition in [
        "correct_image",
        "no_image",
        "blank_image",
        "far_mismatch",
        "hard_mismatch",
    ]:
        rs = by_condition[condition]
        resolved = [r for r in rs if r["parsed_answer"] != "?"]
        correct = [r for r in rs if r["correct"]]

        print(condition)
        print("  rows:", len(rs))
        print("  resolved:", len(resolved))
        print("  unresolved:", len(rs) - len(resolved))
        print("  correct:", len(correct))
        print(
            "  accuracy among all:",
            f"{len(correct) / len(rs):.3f}"
        )
        print(
            "  accuracy among resolved:",
            f"{len(correct) / len(resolved):.3f}"
            if resolved else "NA"
        )

    print()
    print("Unresolved examples:")

    shown = 0
    for r in scored:
        if r["parsed_answer"] == "?":
            print("=" * 70)
            print("case:", r["case_id"])
            print("condition:", r["condition"])
            print("options:", r["options"])
            print("gold:", r["gold_answer"])
            print("response:", r["raw_response"].strip())
            shown += 1
            if shown >= 25:
                break

    print()
    print("Output:", OUTPUT)


if __name__ == "__main__":
    main()
