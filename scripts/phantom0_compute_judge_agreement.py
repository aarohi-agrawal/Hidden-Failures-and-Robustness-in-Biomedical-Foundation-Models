import csv
from pathlib import Path
from collections import Counter

FIELDS = [
    ("acknowledges_missing_or_uncertain", "human_acknowledges_missing_or_uncertain"),
    ("response_mode", "human_response_mode"),
    ("specific_visual_claim", "human_specific_visual_claim"),
]

def cohen_kappa(pairs):
    labels = sorted(set([a for a, b in pairs] + [b for a, b in pairs]))
    n = len(pairs)
    if n == 0:
        return ""

    observed = sum(1 for a, b in pairs if a == b) / n

    auto_counts = Counter(a for a, b in pairs)
    human_counts = Counter(b for a, b in pairs)

    expected = sum((auto_counts[l] / n) * (human_counts[l] / n) for l in labels)

    if expected == 1:
        return 1.0 if observed == 1 else ""

    return (observed - expected) / (1 - expected)

def main():
    scored = {
        r["row_id"]: r
        for r in csv.DictReader(open("annotations/phantom0_all_scored.csv", encoding="utf-8-sig"))
    }

    audit = list(csv.DictReader(open("annotations/phantom0_human_audit.csv", encoding="utf-8-sig")))

    rows = []

    for auto_field, human_field in FIELDS:
        pairs = []
        skipped = 0

        for r in audit:
            row_id = r["row_id"]
            s = scored.get(row_id)

            if not s:
                skipped += 1
                continue

            auto_val = (s.get(auto_field) or "").strip()
            human_val = (r.get(human_field) or "").strip()

            if not auto_val or not human_val:
                skipped += 1
                continue

            pairs.append((auto_val, human_val))

        n = len(pairs)
        matches = sum(1 for a, b in pairs if a == b)
        agreement = matches / n if n else ""

        rows.append({
            "field": auto_field,
            "n_compared": n,
            "n_agree": matches,
            "percent_agreement": "" if agreement == "" else round(agreement, 4),
            "cohens_kappa": "" if n == 0 else round(cohen_kappa(pairs), 4),
            "n_skipped": skipped,
            "auto_distribution": dict(Counter(a for a, b in pairs)),
            "human_distribution": dict(Counter(b for a, b in pairs)),
        })

    Path("metrics").mkdir(exist_ok=True)
    out = "metrics/phantom0_judge_agreement.csv"

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {out}")
    for r in rows:
        print(r["field"], "n=", r["n_compared"], "agreement=", r["percent_agreement"], "kappa=", r["cohens_kappa"], "skipped=", r["n_skipped"])

if __name__ == "__main__":
    main()
