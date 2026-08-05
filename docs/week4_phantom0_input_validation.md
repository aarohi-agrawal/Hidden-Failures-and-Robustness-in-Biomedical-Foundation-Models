# Week 4 Phantom-0 Input Validation

## Purpose

The goal of this validation is to confirm that the Week 4 Phantom-0 replication is testing the intended no-image conditions rather than a runner or input-handling artifact.

Week 4 uses two prompt conditions:

- implicit_no_image
- explicit_missing_image

Both conditions should pass no image. The runner should not silently insert a real image, blank image, or placeholder image.

## Manifest validation

Manifest:

- data/manifests/week4_phantom0_full_eval.csv

Validation result:

- total rows: 400
- unique source IDs: 200
- implicit_no_image rows: 200
- explicit_missing_image rows: 200
- source IDs not appearing twice: 0

Conclusion:

- The manifest contains every Phantom-0 source item once per prompt condition.
- The two prompt conditions are balanced and kept separate.

## Prompt files

Prompt files:

- prompts/phantom0_implicit_no_image_v1.txt
- prompts/phantom0_explicit_missing_v1.txt

## Implicit no-image prompt

The implicit prompt says:

You are a helpful vision-language assistant.

Answer the following visual question.

Question: {question}

Validation note:

- This prompt does not directly state that the image is missing.
- This condition tests whether the model answers as if visual evidence exists when no image is provided.

## Explicit missing-image prompt

The explicit prompt says:

You are a helpful vision-language assistant.

No image is provided.

Answer the following visual question only if it can be answered without the image.

If the image is required, say that you cannot answer because no image was provided.

Question: {question}

Validation note:

- This prompt directly states that no image is provided.
- This condition is a local control for whether the model behaves differently when the missing image is explicitly disclosed.

## Runner inspection

Runner files inspected:

- src/adapters/run_phantom0_week1.py
- src/adapters/run_phantom0_week2_bigger_model.py

Relevant Week 1 runner behavior:

- loads prompt file from prompt_version
- inserts the question with prompt_template.format(question=question)
- builds chat content as text only
- uses content type text
- applies the chat template
- calls the processor with text only

Relevant Week 2 Qwen runner behavior:

- loads prompt file from prompt_version
- inserts the question with prompt_template.format(question=question)
- builds chat content as text only
- uses content type text
- applies the chat template
- calls the processor with text only

Conclusion:

- The inspected Phantom-0 runners do not appear to pass a real image, blank image, or placeholder image.
- The observed processor call is text-only.
- The Week 4 runner should preserve this behavior unless a model-specific issue requires a documented workaround.

## SmolVLM configuration to reuse

Source:

- Week 1 run config

Model:

- HuggingFaceTB/SmolVLM-256M-Instruct

Compute platform:

- CPU

GPU:

- N/A

Prompt versions:

- phantom0_implicit_no_image_v1.txt
- phantom0_explicit_missing_v1.txt

Generation settings:

- temperature: 0.0
- max_new_tokens: 128

Previous run:

- rows attempted: 40
- rows succeeded: 40
- rows failed: 0
- output path: outputs/raw/week1_phantom0_model1.jsonl
- runner: Transformers library

Week 4 note:

- Week 4 should reuse this configuration as closely as practical while scaling from the earlier sample to the full 400-row manifest.

## Qwen configuration to reuse

Source:

- Week 2 and Week 3 larger-model configuration

Model:

- Qwen/Qwen2.5-VL-3B-Instruct

Known runner:

- src/adapters/run_phantom0_week2_bigger_model.py

Generation settings:

- deterministic decoding where supported
- max_new_tokens should remain comparable to Week 1 and Week 2 unless there is a documented reason to change

Status:

- exact runtime software versions and GPU details still need to be recorded during the Week 4 run.

## Rendered prompt inspection plan

Before full inference, inspect at least five rendered prompts for each condition.

Minimum check:

- 5 implicit_no_image prompts
- 5 explicit_missing_image prompts

Checks:

1. question text matches the manifest
2. prompt version matches the condition
3. implicit prompt does not mention missing image
4. explicit prompt clearly says no image is provided
5. no image object is included in the chat message

## Small validation run plan

Before full inference, run a small validation set.

Planned test:

- 5 Phantom-0 source items
- 2 conditions
- 2 models
- expected 20 output rows

Checks:

1. every input row produces one output row
2. model and condition metadata are correct
3. raw responses are saved
4. errors are saved rather than silently dropped
5. no image object is passed for either condition
6. output rows can be converted into Student C annotation input format

## Current conclusion

Input validation is partially complete.

Completed:

- full Week 4 manifest validated
- prompt files inspected
- old Phantom-0 runners inspected
- no-image behavior appears to use text-only processor calls

Still needed:

- inspect rendered prompts from the Week 4 runner
- run small validation set
- record exact Week 4 runtime software versions
- record exact model and processor revisions where available
- record GPU type for Qwen run