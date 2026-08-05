# Week 5 Data Review

## Overview

Week 5 builds a controlled evidence-difficulty benchmark containing 40 MMVP cases.

Each case contains five evaluation conditions:

- correct_image
- no_image
- blank_image
- far_mismatch
- hard_mismatch

The final evaluation manifest contains 40 cases × 5 conditions = 200 rows.

The goal is to evaluate multimodal foundation model behavior when visual evidence is correct, missing, blank, unrelated, or misleading.

## Case Selection

The Week 5 candidate pool contains new MMVP cases that were not used in previous Week 2 or Week 3 evaluations.

Selection criteria:

- Cases were manually reviewed.
- Gold answers were verified.
- Cases were sampled across different visual categories.
- Ambiguous cases were excluded or replaced using reserve cases.

Final dataset:

- Primary cases: 40
- Reserve cases: 10

The selected cases are stored in:

data/manifests/week5_evidence_ladder_seed.csv

Reserve cases are stored in:

data/manifests/week5_reserve_cases.csv

A validation check confirmed that no selected Week 5 cases overlap with previous Week 2 or Week 3 cases.

## Category Coverage

The final 40-case distribution is:

| Category | Count |
|---|---:|
| Animals | 10 |
| Food | 7 |
| Object | 5 |
| Human/Object | 4 |
| Vehicle | 3 |
| Human | 3 |
| Technology Devices | 3 |
| Landscape | 1 |
| Pattern/Counting | 1 |
| Furniture | 1 |
| House | 1 |
| Character | 1 |

The dataset covers multiple visual reasoning categories including object recognition, animal reasoning, human interaction, scene understanding, and fine-grained visual attributes.

## Blank Image Generation

A matched blank image was created for every primary case.

Generation rules:

- Original image width and height were preserved.
- Images were generated in RGB format.
- All blank images use the same pixel value: RGB(255,255,255).

Generated images are stored in:

data/generated/week5_blank_images/

Validation included:

- confirming image dimensions
- confirming file creation
- generating SHA256 checksums

The validation report is stored in:

data/generated/week5_blank_images/week5_blank_image_report.csv

## Far Mismatch Construction

Far mismatches were created by pairing each source case with a clearly unrelated image.

Requirements:

- The mismatched image should not provide evidence for answering the original question.
- The mismatch should be visually unrelated.
- Each mismatch contains a source ID and explanation.

The final far mismatch map contains 40 validated mismatches:

data/manifests/week5_far_mismatch_map.csv

## Hard Mismatch Construction

Hard mismatches were created using visually plausible images from similar categories or task types.

Construction rules:

- Similarity was used only for candidate retrieval.
- Final mismatch decisions were manually verified.
- Each pair received a human difficulty rating from 1 to 3.

Difficulty scale:

1 = easy mismatch  
2 = plausible mismatch requiring inspection  
3 = difficult mismatch with strong visual similarity

Final difficulty distribution:

| Rating | Count |
|---|---:|
| 1 | 2 |
| 2 | 30 |
| 3 | 9 |

The final hard mismatch map contains 40 validated mismatches:

data/manifests/week5_hard_mismatch_map.csv

## Manifest Validation

The final evidence ladder manifest contains five conditions for each of the 40 cases.

Manifest:

data/manifests/week5_evidence_ladder_eval.csv

Condition counts:

| Condition | Count |
|---|---:|
| correct_image | 40 |
| no_image | 40 |
| blank_image | 40 |
| far_mismatch | 40 |
| hard_mismatch | 40 |

Total rows:

200

## Validation Checks Completed

The following checks were completed:

- Verified 40 primary cases.
- Verified 10 reserve cases.
- Confirmed no overlap with previous weeks.
- Verified gold answers.
- Verified blank image generation.
- Verified image dimensions and checksums.
- Verified mismatch source IDs.
- Verified far mismatch explanations.
- Verified hard mismatch difficulty ratings.
- Verified final manifest contains exactly 200 rows.

## Ambiguous Cases

No unresolved ambiguous cases remain.

All candidate cases were manually reviewed before freezing the Week 5 manifest.

Reserve cases remain available if future exclusions require replacements.