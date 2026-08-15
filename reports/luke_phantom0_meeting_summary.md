# Phantom-0 Week 5 Meeting Summary

## Status

- Full raw output set complete: 1,200 total outputs.
- Models: SmolVLM, Qwen-3B, Qwen-7B.
- Conditions: implicit no-image and explicit missing-image.
- Automatic judge completed with one retry pass.
- 1,196 / 1,200 rows parsed successfully.
- 4 judge parse failures remain documented in `annotations/phantom0_judge_parse_failures.csv`.
- Results below are automatic-judge results and still require human-audit validation.

## Primary Results

| Model | Condition | N valid | MIRAGE | Recognition | Abstain | Hard MIRAGE | Soft MIRAGE |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen-3B | explicit | 198 | 5.1% | 95.0% | 96.0% | 3.5% | 0.5% |
| Qwen-3B | implicit | 183 | 22.4% | 77.6% | 79.2% | 10.4% | 2.7% |
| Qwen-7B | explicit | 196 | 3.6% | 96.4% | 96.9% | 2.0% | 1.0% |
| Qwen-7B | implicit | 181 | 18.8% | 81.2% | 89.5% | 5.0% | 2.8% |
| SmolVLM | explicit | 194 | 91.8% | 8.2% | 10.3% | 75.8% | 10.3% |
| SmolVLM | implicit | 190 | 100.0% | 0.0% | 0.5% | 85.8% | 7.4% |

## Prompt Effects
These are explicit minus implicit differences. Negative MIRAGE means the explicit missing-image prompt lowered MIRAGE.

| Model | MIRAGE Δ | Recognition Δ | Abstain Δ | Hard MIRAGE Δ | Soft MIRAGE Δ |
|---|---:|---:|---:|---:|---:|
| Qwen-3B | -17.3% | 17.3% | 16.7% | -6.8% | -2.2% |
| Qwen-7B | -15.2% | 15.2% | 7.4% | -2.9% | -1.7% |
| SmolVLM | -8.2% | 8.2% | 9.8% | -10.0% | 2.9% |

## Qwen Family Comparison
- Comparison: Qwen-7B minus Qwen-3B under implicit condition.
- MIRAGE difference: -3.6%
- Recognition difference: 3.6%
- Hard MIRAGE difference: -5.4%
- Soft MIRAGE difference: 0.0%

## Caveats
- These are not final claims until the human audit agreement is computed.
- Do not claim that scale caused any improvement.
- Do not describe Qwen as perfect; use the exact rates.
- The explicit condition is a control, not the primary MIRAGE replication condition.