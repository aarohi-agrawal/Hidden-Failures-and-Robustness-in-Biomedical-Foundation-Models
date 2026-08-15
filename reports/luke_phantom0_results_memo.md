# Luke Phantom-0 Results Memo

## Status

The full Phantom-0 quantitative run is complete at the raw-output and automatic-scoring level.

Dataset design:
- 200 Phantom-0 questions
- 2 prompt conditions
- 3 models
- 1,200 total outputs

Models:
- SmolVLM
- Qwen-3B
- Qwen-7B

Conditions:
- implicit no-image
- explicit missing-image

Automatic scoring was completed with the frozen judge prompts. After one retry pass, 1,196 of 1,200 rows parsed successfully. The remaining 4 parse failures are documented and excluded from valid-rate denominators.

These results are automatic-judge results and should be treated as preliminary until human-audit agreement is computed.

## Three Most Important Numbers

1. SmolVLM implicit MIRAGE rate was 1.000, meaning the automatic judge found MIRAGE behavior on all valid implicit no-image rows.
2. Qwen-3B implicit MIRAGE rate was 0.224, much lower than SmolVLM under the same condition.
3. Qwen-7B implicit MIRAGE rate was 0.1878, slightly lower than Qwen-3B under the same condition.

## Does MIRAGE reproduce across our models?

Yes, but not uniformly. The implicit no-image condition shows that MIRAGE behavior appears strongly in SmolVLM and still appears in Qwen-3B and Qwen-7B at lower rates.

This supports the claim that missing-image behavior differs substantially across these model configurations.

## What changes under the explicit missing-image condition?

The explicit missing-image prompt lowers MIRAGE for all three models.

SmolVLM changes the most:
- implicit MIRAGE: 1.000
- explicit MIRAGE: 0.9175

Qwen-3B:
- implicit MIRAGE: 0.224
- explicit MIRAGE: 0.0505

Qwen-7B:
- implicit MIRAGE: 0.1878
- explicit MIRAGE: 0.0357

This suggests that missing-evidence behavior is sensitive to prompt framing. The explicit condition should be interpreted as a control, not the primary MIRAGE replication condition.

## What can we say about Qwen-3B vs Qwen-7B?

Under the implicit condition, Qwen-7B has a lower MIRAGE rate than Qwen-3B:
- Qwen-3B implicit MIRAGE: 0.224
- Qwen-7B implicit MIRAGE: 0.1878

This suggests that Qwen-7B was somewhat more evidence-aware in this setup. However, this should not be interpreted as proof that parameter count caused the difference. Other configuration, training, decoding, or checkpoint differences may also matter.

## Hard MIRAGE

Hard MIRAGE was highest for SmolVLM:
- SmolVLM implicit hard MIRAGE: 0.8579
- SmolVLM explicit hard MIRAGE: 0.7577

Qwen hard MIRAGE was lower:
- Qwen-3B implicit hard MIRAGE: 0.1038
- Qwen-7B implicit hard MIRAGE: 0.0497

This suggests that SmolVLM more often produced unsupported specific visual claims when visual evidence was missing.

## Limitations

1. These are automatic-judge results and still need human-audit validation.
2. Four judge parse failures remain after retry and are excluded from valid-rate denominators.
3. The benchmark does not identify the internal mechanism behind MIRAGE behavior.
4. The Qwen-3B vs Qwen-7B comparison should not be treated as causal evidence about scale.
5. Explicit missing-image results are a control condition, not the primary replication setting.

## Next Step

The next step is to complete the human audit and compute judge-human agreement for:
- acknowledges_missing_or_uncertain
- response_mode
- specific_visual_claim

If judge agreement is strong, the automatic results can support the final table. If agreement is weak for a headline field, that metric should not be reported as a reliable full-table result without adjustment.
## Human Audit Validation

A stratified human audit was completed across the model-condition cells. The human labels were compared against the automatic GPT-5.6 Luna judge outputs for the three observable fields used in scoring.

Judge agreement results:

| Field | N Compared | Percent Agreement | Cohen's Kappa | Skipped |
|---|---:|---:|---:|---:|
| acknowledges_missing_or_uncertain | 179 | 0.9106 | 0.8163 | 1 |
| response_mode | 180 | 0.8111 | 0.6643 | 0 |
| specific_visual_claim | 180 | 0.8389 | 0.6041 | 0 |

The strongest agreement was for missing-evidence acknowledgement, which is the primary field for MIRAGE versus recognition. Agreement was lower but still usable for response mode and specific visual claim. The specific visual claim field should be interpreted with the most caution because it is more subjective and directly affects the hard versus soft MIRAGE split.

Based on this audit, the automatic judge appears reliable enough for the headline acknowledgement/MIRAGE table, but hard and soft MIRAGE should be reported with a caveat that they depend on the more subjective specific_visual_claim field.

