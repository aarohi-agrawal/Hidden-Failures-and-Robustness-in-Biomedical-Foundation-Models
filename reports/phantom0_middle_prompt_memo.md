# Phantom-0 Middle Prompt Experiment Memo

## Goal

The middle-prompt experiment tests whether models can follow a general evidence-sufficiency instruction without being directly told that no image is provided.

The prompt spectrum is:

- implicit: visual question with no image and no warning
- middle: visual question with an evidence-checking instruction, but no explicit "No image is provided" line
- explicit: visual question with the line "No image is provided"

## Main Result

The middle prompt strongly reduced MIRAGE for Qwen models, but only slightly reduced MIRAGE for SmolVLM.

| Model | Implicit MIRAGE | Middle MIRAGE | Explicit MIRAGE |
|---|---:|---:|---:|
| SmolVLM | 1.0000 | 0.9725 | 0.9175 |
| Qwen-3B | 0.2240 | 0.0615 | 0.0505 |
| Qwen-7B | 0.1878 | 0.0051 | 0.0357 |

## Interpretation

For Qwen-3B, the middle prompt is nearly as effective as the explicit prompt. MIRAGE drops from 22.4% in the implicit condition to 6.15% in the middle condition, compared with 5.05% in the explicit condition.

For Qwen-7B, the middle prompt performs even better than the explicit prompt. MIRAGE drops from 18.78% implicit to 0.51% middle, compared with 3.57% explicit.

This suggests that Qwen models are not only reacting to the exact phrase "No image is provided." They can also respond to a broader evidence-sufficiency instruction.

SmolVLM remains highly vulnerable across all three conditions. Its MIRAGE rate decreases from 100% implicit to 97.25% middle and 91.75% explicit, but the model still usually fails to recognize missing visual evidence.

## Hard MIRAGE

| Model | Implicit Hard MIRAGE | Middle Hard MIRAGE | Explicit Hard MIRAGE |
|---|---:|---:|---:|
| SmolVLM | 0.8579 | 0.7143 | 0.7577 |
| Qwen-3B | 0.1038 | 0.0056 | 0.0354 |
| Qwen-7B | 0.0497 | 0.0000 | 0.0204 |

The middle prompt especially reduces hard MIRAGE for Qwen models. Qwen-7B has 0 hard MIRAGE in the middle condition among valid/scorable rows.

## Caveat

The middle condition had 32 judge parse failures after one retry. These rows were documented and excluded from valid denominators. The main interpretation should focus on the large direction of change rather than tiny differences between middle and explicit.

## Research Takeaway

The project now has a stronger prompt-sensitivity story. The results suggest that evidence-checking instructions can substantially reduce missing-image MIRAGE for stronger Qwen models, even without explicitly saying that no image is provided. However, this intervention does not solve the issue for SmolVLM.

The next direction is to inspect representative middle-prompt examples, especially:
- Qwen cases where the middle prompt succeeds but implicit fails
- Qwen cases where middle still fails
- SmolVLM cases where even explicit or middle prompting fails
