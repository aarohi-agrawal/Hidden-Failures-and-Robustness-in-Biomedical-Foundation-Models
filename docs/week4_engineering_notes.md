# Week 4 Engineering Notes

## Summary

Week 4 focused on completing the Phantom-0 replication package for the two primary open models used by the group: SmolVLM and Qwen.

Final status:
- Full Week 4 Phantom-0 manifest created and validated.
- SmolVLM full run completed.
- Qwen full run completed.
- Annotation input CSV prepared for Student C.

## Manifest

Manifest:
- `data/manifests/week4_phantom0_full_eval.csv`

Validation:
- Total rows: 400
- Unique source IDs: 200
- `implicit_no_image`: 200 rows
- `explicit_missing_image`: 200 rows
- Each source ID appears exactly twice.

## Runner

Runner:
- `src/adapters/run_phantom0_week4.py`

Important runner behavior:
- Loads prompt based on `prompt_version`.
- Inserts the manifest question into the prompt template.
- Uses text-only chat content.
- Calls processor with text only.
- Does not pass a real image, blank image, or placeholder image.
- Writes one JSONL row for every attempted manifest row.
- Preserves raw responses and errors.

## SmolVLM run history

Initial full SmolVLM GPU attempt:
- Output was written but all 400 rows failed.
- Error cause: CUDA out-of-memory on a busy GPU.
- Failed output was preserved as:
  - `outputs/raw/week4_phantom0_smolvlm_FAILED_oom.jsonl`

Final SmolVLM run:
- Rerun with CUDA disabled to match the earlier CPU configuration.
- Final output:
  - `outputs/raw/week4_phantom0_smolvlm.jsonl`
- Rows attempted: 400
- Rows written: 400
- Rows failed: 0

## Qwen run history

Initial Qwen attempt:
- Small validation test succeeded.
- First full interactive run was interrupted around case 79 due to session/connection termination.

Batch rerun:
- The first `sbatch` attempt failed because Slurm used `/bin/sh`, where `source` was not available.
- The command was fixed by wrapping the run in `bash -lc`.
- Final Qwen run completed successfully through `sbatch`.

Final Qwen output:
- `outputs/raw/week4_phantom0_qwen.jsonl`
- Rows attempted: 400
- Rows written: 400
- Rows failed: 0
- Time elapsed: approximately 786 seconds

## Final output files

Raw outputs:
- `outputs/raw/week4_phantom0_smolvlm.jsonl`
- `outputs/raw/week4_phantom0_qwen.jsonl`

Student C annotation/classification input:
- `annotations/week4_phantom0_annotation_input.csv`

## Handoff notes for Student C

The annotation input file preserves:
- `run_id`
- `case_id`
- `source_id`
- `domain`
- `category`
- `risk_level`
- `question_type`
- `model_name`
- `condition`
- `prompt_condition`
- `prompt_version`
- `question`
- `raw_response`
- `run_status`
- `error`

Raw responses were not overwritten with labels. Student C can use this file for automated classification and manual audit.