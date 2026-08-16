# MMVP Evidence Integrity — Quantitative Memo

## Evaluation Summary

This evaluation measures evidence integrity and counterfactual robustness of
`HuggingFaceTB/SmolVLM-256M-Instruct` across five evidence conditions.

- Model: `HuggingFaceTB/SmolVLM-256M-Instruct`
- Revision: `main`
- Prompt version: `mmvp_evidence_integrity_v1`
- Cases: 40
- Conditions per case: 5
- Total evaluations: 200
- Generation temperature: 0.0
- Sampling: disabled
- Maximum new tokens: 128

## Condition-Level Accuracy

| Condition | Correct | Total | Accuracy |
|---|---:|---:|---:|
| Correct image | 22 | 40 | 55.0% |
| No image | 22 | 40 | 55.0% |
| Blank image | 16 | 40 | 40.0% |
| Far mismatch | 19 | 40 | 47.5% |
| Hard mismatch | 22 | 40 | 55.0% |
| **Overall** | **101** | **200** | **50.5%** |

## Case-Level Transitions

Compared with the corresponding `correct_image` condition:

| Condition | Degraded | Improved | Same |
|---|---:|---:|---:|
| No image | 9 | 9 | 22 |
| Blank image | 13 | 7 | 20 |
| Far mismatch | 12 | 9 | 19 |
| Hard mismatch | 6 | 6 | 28 |

The blank-image condition produced the largest number of degradations relative
to the correct-image baseline (13 of 40 cases). Far mismatches produced 12
degradations, while no-image produced 9 and hard mismatch produced 6.

## Evidence-Integrity Observations

The correct-image condition achieved 55.0% accuracy. Removing the image did
not change aggregate accuracy, which remained at 55.0%.

Performance decreased to 40.0% with a blank image and to 47.5% with a far
mismatch. Hard mismatch accuracy was 55.0%.

These results show that the model does not consistently require valid visual
evidence to produce an answer. In particular, the no-image condition matched
the correct-image accuracy, while the model also retained substantial accuracy
under mismatched-image conditions.

The case-level transitions provide additional evidence of instability:
12 cases degraded under far mismatch and 13 degraded under blank images.
However, some cases also improved relative to the correct-image condition,
indicating that aggregate accuracy alone does not fully characterize
counterfactual behavior.

## Data Integrity

The Week 5 evaluation set contains 40 verified source/partner pairs. All
selected pairs have opposite official and partner gold answers, with no
duplicate source IDs, partner IDs, or pair IDs.

The output integrity checks passed for all five conditions:

- Correct image: 40 rows
- No image: 40 rows
- Blank image: 40 rows
- Far mismatch: 40 rows
- Hard mismatch: 40 rows
- Unique case IDs: 40
- Each case has five conditions
- Gold-answer consistency: PASS
- Image-path/condition checks: PASS
- Mismatch-source checks: PASS
- Runtime errors: 0
- Empty responses: 0
- Duplicate case/condition pairs: 0

## Interpretation

The primary result is that SmolVLM-256M achieved only 55.0% accuracy when
provided with the correct image. Its performance remained 55.0% without an
image, fell to 40.0% with a blank image, and was 47.5% with far mismatched
images. Hard mismatches returned to 55.0%.

Accordingly, these results should be interpreted as evidence of limited and
inconsistent dependence on visual evidence rather than as a simple monotonic
relationship between evidence quality and accuracy.

The evaluation is designed to expose whether model answers track the evidence
available in the input. The observed condition-level and case-level results
indicate that the model can produce answers that remain correct even when
relevant visual evidence is absent, while also producing substantial errors
when evidence is unavailable or replaced.

## Limitations

This memo reports results for one model, one model revision, one prompt
version, and 40 evaluation cases. The results therefore characterize this
Week 5 evaluation rather than establishing general performance across
biomedical foundation models.

Human evidence-awareness judgments have not yet been completed. The
`annotations/mmvp_human_audit.csv` file is therefore retained as a review
template and should not be interpreted as completed human annotation.

## Reproducibility

Primary evaluation output:

`outputs/mmvp_evidence_integrity_all.jsonl`

Long-form metrics:

`metrics/mmvp_results_long.csv`

Valid-evidence subset:

`metrics/mmvp_valid_evidence_results.csv`

Invalid/absent-evidence subset:

`metrics/mmvp_invalid_evidence_results.csv`

Evaluation manifest:

`data/manifests/mmvp_40pair_frozen.csv`

Far-mismatch mapping:

`data/manifests/mmvp_far_mismatch_map.csv`

Figures:

- `figures/mmvp_counterfactual_following.png`
- `figures/mmvp_evidence_awareness.png`
