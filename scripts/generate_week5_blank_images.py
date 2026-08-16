from pathlib import Path
import hashlib

import pandas as pd
from PIL import Image

MMVP_DIR = Path("data/mmvp/MMVP Images")


SEED_CSV = Path("data/manifests/week5_evidence_ladder_seed.csv")
OUTPUT_DIR = Path("data/generated/week5_blank_images")
REPORT_CSV = OUTPUT_DIR / "week5_blank_image_report.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

seed = pd.read_csv(SEED_CSV)

records = []

for idx, row in enumerate(seed.itertuples(index=False), start=1):

    case_id = int(row.case_id)

    image_path = MMVP_DIR / f"{case_id}.jpg"

    if not image_path.exists():
        raise FileNotFoundError(image_path)

    img = Image.open(image_path)

    width, height = img.size

    blank = Image.new(
        mode="RGB",
        size=(width, height),
        color=(255, 255, 255),
    )

    filename = f"mmvp_w5_{idx:03d}_blank.png"

    output_path = OUTPUT_DIR / filename

    blank.save(output_path)

    sha256 = hashlib.sha256(output_path.read_bytes()).hexdigest()

    records.append(
        {
            "bundle_index": idx,
            "case_id": case_id,
            "filename": filename,
            "width": width,
            "height": height,
            "sha256": sha256,
        }
    )

report = pd.DataFrame(records)

report.to_csv(REPORT_CSV, index=False)

print()
print(f"Generated {len(report)} blank images.")
print(f"Saved to: {OUTPUT_DIR}")
print(f"Report: {REPORT_CSV}")
