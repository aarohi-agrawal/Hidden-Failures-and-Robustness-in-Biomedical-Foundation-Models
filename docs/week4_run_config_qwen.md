# Week 4 Run Config: Qwen

## Model

- Model: `Qwen/Qwen2.5-VL-3B-Instruct`
- Role in study: primary larger/open model
- Source configuration: reused Week 2/Week 3 Qwen configuration as closely as practical

## Input manifest

- Manifest: `data/manifests/week4_phantom0_full_eval.csv`
- Source benchmark: Phantom-0
- Total manifest rows for this model: 400
- Conditions:
  - `implicit_no_image`: 200 rows
  - `explicit_missing_image`: 200 rows

## Prompt versions

- `phantom0_implicit_no_image_v1`
- `phantom0_explicit_missing_v1`

## Image handling

- No real image was passed.
- No blank image was passed.
- No placeholder image was passed.
- Runner used text-only chat content.
- Processor call used text only.

## Generation settings

- `max_new_tokens`: 128
- Temperature recorded as 0.0 / deterministic-style generation
- Runner: `src/adapters/run_phantom0_week4.py`

## Output

- Final output path: `outputs/raw/week4_phantom0_qwen.jsonl`
- Rows attempted: 400
- Rows written: 400
- Rows failed: 0

## Runtime notes

The first full Qwen attempt was run interactively and was interrupted around case 79 due to session/connection termination. The final successful run was submitted through `sbatch` so it did not depend on the browser or terminal connection.

Final successful Qwen run:
- Rows attempted: 400
- Rows written: 400
- Rows failed: 0
- Time elapsed: approximately 786 seconds