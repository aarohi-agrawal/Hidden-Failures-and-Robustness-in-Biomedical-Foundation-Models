# Week 2 Engineering Notes

## Phantom-0 bigger-model run

Input manifest: data/manifests/week2_phantom0_bigger_model_eval.csv  
Test manifest: data/manifests/week2_phantom0_bigger_model_test6.csv  
Output path: outputs/raw/week2_phantom0_bigger_model.jsonl  
Model: Qwen/Qwen2.5-VL-3B-Instruct  
Status: blocked pending compute approval/instructions  

## Manifest validation

Rows: 40  
Prompt conditions:
- implicit_no_image: 20
- explicit_missing_image: 20

include_in_eval:
- yes: 40

## Current blocker

I was warned not to run heavy model inference locally. Waiting for mentor/team confirmation on whether to use Unity/lab compute or whether local inference is explicitly approved.

## Planned run order

1. Log into approved compute platform.
2. Confirm GPU with nvidia-smi.
3. Pull latest repo.
4. Install requirements.
5. Run 6-row test manifest.
6. Confirm JSONL schema is annotatable.
7. Run full 40-row manifest.
8. Push outputs/raw/week2_phantom0_bigger_model.jsonl.
9. Report rows attempted/succeeded/failed.
10. Stop/destroy compute instance if applicable.