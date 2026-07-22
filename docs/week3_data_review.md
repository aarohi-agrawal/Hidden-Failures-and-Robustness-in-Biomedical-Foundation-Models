# Week 3 Data Review

## Files created

- data/manifests/week2_mmvp_used_ids.csv
- data/manifests/week3_mmvp_seed.csv
- data/manifests/week3_mismatch_map.csv
- data/manifests/week3_mmvp_eval.csv
- data/generated/week3_blank_images/
- docs/week3_mismatch_review_contact_sheet.png

## Summary

- New bundles: 16
- Manifest rows: 64
- Conditions: image_present, no_image, blank_image, mismatched_image
- Prompt version: mmvp_evidence_integrity_v1

## Selection procedure

Week 2 source IDs were excluded. Sixteen new examples were selected across the MMVP source-ID range rather than by taking adjacent rows.

## Shared image path

/work/pi_cics-ur_umass_edu/mirage_shared/data/mmvp/MMVP Images

## Blank images

Blank images were generated with the same width and height as the original image whenever practical.

Folder:

data/generated/week3_blank_images/

Pixel value:

RGB(255,255,255)

## Mismatch construction

Mismatched images were assigned using a deterministic +8 rotation across the 16 selected bundles.

Review contact sheet:

docs/week3_mismatch_review_contact_sheet.png

## Validation notes

Validation errors before manual mismatch review:

- None

Manual mismatch review was completed by Student A. All mismatches were marked reviewed in data/manifests/week3_mismatch_map.csv.
