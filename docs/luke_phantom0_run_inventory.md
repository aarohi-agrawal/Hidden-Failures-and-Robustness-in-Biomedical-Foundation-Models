# Luke Phantom-0 Run Inventory

## Purpose

This document inventories the completed and missing Phantom-0 Week 5 model-condition cells before quantitative scoring. Per the Week 5 plan, completed cells should be reused and only missing cells should be run.

## Dataset

- Dataset: Phantom-0
- Source questions: 200
- Conditions:
  - `implicit_no_image`
  - `explicit_missing_image`
- Planned maximum table:
  - 200 questions × 2 conditions × 3 models = 1,200 outputs

## Completed runs

### SmolVLM

- Model/checkpoint: `HuggingFaceTB/SmolVLM-256M-Instruct`
- Output file: `outputs/raw/week4_phantom0_smolvlm.jsonl`
- Rows: 400
- Conditions:
  - `implicit_no_image`: 200
  - `explicit_missing_image`: 200
- Final error count: 0
- Notes: Final successful run used CUDA disabled / CPU-only after an earlier GPU out-of-memory attempt.

### Qwen 3B

- Model/checkpoint: `Qwen/Qwen2.5-VL-3B-Instruct`
- Output file: `outputs/raw/week4_phantom0_qwen.jsonl`
- Rows: 400
- Conditions:
  - `implicit_no_image`: 200
  - `explicit_missing_image`: 200
- Final error count: 0
- Notes: Final successful run was completed through `sbatch` after an interrupted interactive run.

## Missing runs

### Qwen 7B

- Model/checkpoint: `Qwen/Qwen2.5-VL-7B-Instruct`
- Needed rows: 400
- Conditions needed:
  - `implicit_no_image`: 200
  - `explicit_missing_image`: 200
- Status: not yet run / needs confirmation

## Judge prompts frozen

- MIRAGE-compatible judge prompt:
  - `prompts/judges/phantom0_mirage_judge_v1.txt`
- Behavioral judge prompt:
  - `prompts/judges/phantom0_behavior_judge_v1.txt`

## Blocking questions before scoring

1. Do we have project access to GPT-5 for the automatic judge?
2. Should the Qwen 7B checkpoint be exactly `Qwen/Qwen2.5-VL-7B-Instruct`?
3. Should Qwen 7B be run on the same Week 4 runner with the same manifest and prompt versions?

## Current status

- SmolVLM complete.
- Qwen 3B complete.
- Qwen 7B appears to be the only missing model cell.
- Scoring should not begin until judge access and Qwen 7B status are confirmed.

## Qwen 7B status update

- Model/checkpoint: `Qwen/Qwen2.5-VL-7B-Instruct`
- Planned output file: `outputs/raw/week5_phantom0_qwen7b.jsonl`
- Needed rows: 400
- Conditions:
  - `implicit_no_image`: 200
  - `explicit_missing_image`: 200
- A 4-row validation run completed successfully with 0 errors.
- Full 400-row run submitted through `sbatch`.
- Status: running / pending validation.
- Notes: The 4-row test took approximately 270 seconds, so the full 400-row run may take several hours because Qwen-7B appears to use GPU plus CPU offload on the available hardware.

## Qwen 7B full-run attempt

- Model/checkpoint: `Qwen/Qwen2.5-VL-7B-Instruct`
- Planned output file: `outputs/raw/week5_phantom0_qwen7b.jsonl`
- Slurm job ID: `62851019`
- GPU allocated: NVIDIA A16, approximately 15GB VRAM
- A 4-row validation run completed successfully with 0 errors.
- The full 400-row run was submitted through `sbatch`.
- After more than 5 hours of runtime, the output file was still 0 bytes / 0 rows.
- The log showed the model loaded and that some parameters were offloaded to CPU.
- Status: full Qwen-7B run unresolved / likely stalled under current A16 + CPU-offload setup.
- Protocol decision: do not change checkpoint, quantization, or generation setup silently before team confirmation.

## Qwen 7B Phantom-0 run

- Model/checkpoint: `Qwen/Qwen2.5-VL-7B-Instruct`
- Output file: `outputs/raw/week5_phantom0_qwen7b.jsonl`
- Rows: 400
- Conditions:
  - `implicit_no_image`: 200
  - `explicit_missing_image`: 200
- Status: completed
- Validation: 400 rows, success rows only, 0 errors
- Notes: Full run completed successfully on Unity after extended runtime on A16 GPU with CPU offload. It took 5.47 hours