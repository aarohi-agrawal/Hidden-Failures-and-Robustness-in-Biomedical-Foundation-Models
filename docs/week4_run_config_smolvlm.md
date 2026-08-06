# Week 4 Run Config: SmolVLM

## Model

- Model: `HuggingFaceTB/SmolVLM-256M-Instruct`
- Role in study: primary small/open model
- Source configuration: reused Week 1 SmolVLM configuration as closely as practical

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

- Final output path: `outputs/raw/week4_phantom0_smolvlm.jsonl`
- Rows attempted: 400
- Rows written: 400
- Rows failed: 0

## Notes

The first full SmolVLM attempt on GPU wrote 400 rows but all rows failed due to CUDA out-of-memory on a busy GPU. That failed output was preserved separately as `outputs/raw/week4_phantom0_smolvlm_FAILED_oom.jsonl`.

Because the Week 1 SmolVLM run used CPU, the final Week 4 SmolVLM run was rerun with CUDA disabled. The CPU-only run completed successfully with 400 rows and 0 errors.