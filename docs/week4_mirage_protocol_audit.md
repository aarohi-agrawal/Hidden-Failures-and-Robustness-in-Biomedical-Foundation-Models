# Week 4 MIRAGE / Phantom-0 Protocol Audit

## Purpose

The goal of this audit is to compare the original MIRAGE Phantom-0 protocol with our local Week 4 open-model replication.

Week 4 asks whether MIRAGE no-image findings extend to the SmolVLM and Qwen configurations used by our group. The main risk is accidentally measuring an input-handling or runner difference rather than actual model behavior.

## Source benchmark

- Benchmark: Phantom-0
- Source repository: https://github.com/masadi-99/MIRAGE
- Local source file used: `data/raw/mirage/phantom_0.json`
- Local Week 4 manifest: `data/manifests/week4_phantom0_full_eval.csv`
- Released item count used locally: 200
- Week 4 manifest rows: 400
- Conditions:
  - `implicit_no_image`
  - `explicit_missing_image`

The local manifest includes every Phantom-0 item once under each prompt condition.

## MIRAGE protocol summary

From the MIRAGE repository README, MIRAGE studies how vision-language models respond when images are silently removed from visual question answering tasks. The repository introduces Phantom-0 as a benchmark for measuring mirage rates.

The MIRAGE repository includes Phantom-0 under `data/phantom_0/`.

The original MIRAGE experiments include:
- Mirage rate evaluation: how often models describe non-existent images without acknowledging absence.
- Mirage vs guess mode: comparison between silently removed images and explicitly missing-image/guess-style conditions.

## Local Week 4 protocol

Our local Week 4 protocol is an open-model extension rather than an exact closed-model reproduction.

### Local models

Primary models:
- SmolVLM configuration from Week 1
- Qwen configuration from Weeks 2-3

Exact model identifiers and revisions will be recorded in:
- `docs/week4_run_config_smolvlm.md`
- `docs/week4_run_config_qwen.md`

### Local prompt conditions

The Week 4 manifest keeps the two prompt conditions separate.

#### implicit_no_image

Prompt version:
- `phantom0_implicit_no_image_v1`

Purpose:
- Test model behavior when the question is presented without an image and without explicitly warning that the image is missing.

#### explicit_missing_image

Prompt version:
- `phantom0_explicit_missing_v1`

Purpose:
- Local control condition where the model is explicitly told or cued that visual evidence is missing.

Important:
- These two conditions are not mixed under one prompt version.

## Image handling audit

The expected input behavior for both Week 4 conditions is:

- No real image should be passed.
- No blank image should be passed.
- No placeholder image should be silently inserted.
- The model runner should send text-only input for no-image rows unless a model-specific implementation requires a documented workaround.

This will be validated in:
- `docs/week4_phantom0_input_validation.md`

## Local runner comparison

Local runner files to compare:
- `src/adapters/run_phantom0_week1.py`
- `src/adapters/run_phantom0_week2_bigger_model.py`
- Week 4 runner file, if created or adapted

Items to verify:
- how prompts are loaded
- how questions are inserted
- how no-image rows are represented
- whether the processor receives an image object
- whether a placeholder image is used anywhere
- whether one output row is saved for every input row
- whether failures are saved instead of silently dropped

## Generation settings

To be filled from local run configs and runners.

Fields to record:
- temperature
- do_sample
- max_new_tokens
- seed, if used
- retry behavior
- truncation behavior
- device / dtype
- GPU type

## Classification / judge differences

The original MIRAGE Phantom-0 evaluation uses a judge/classification procedure to measure mirage behavior.

Our Week 4 local output handoff will not overwrite raw responses with labels. Instead, outputs will be converted into:
- `annotations/week4_phantom0_annotation_input.csv`

Student C will calibrate the automated or LLM-assisted first-pass classifier and manual audit procedure.

Important difference:
- Our local study separates raw model generation from later annotation/classification.

## Known differences from original MIRAGE

Current known differences:
1. We are using open Hugging Face models instead of the original closed-model set used in parts of MIRAGE.
2. We are using local runners in this project repo rather than the MIRAGE pipeline directly.
3. We are testing two prompt conditions: implicit no-image and explicit missing-image.
4. We are preserving raw outputs for Student C rather than only reporting final judged rates.
5. Our model comparison should be described as a model-family/configuration comparison, not as a causal claim about scale.

## Items still needing verification

- Exact MIRAGE commit hash used for `phantom_0.json`
- Exact original MIRAGE prompt wording
- Exact original judge prompt or classification code
- Exact generation settings used in the MIRAGE paper runs
- Whether the original protocol omitted image objects or used a particular image-mode setting internally
- Exact local SmolVLM model revision
- Exact local Qwen model revision
- Exact local software versions and GPU type

## Current status

- Full Phantom-0 source file identified.
- Week 4 full manifest created.
- Manifest contains 200 source items and 400 condition rows.
- Next step is input validation for both model runners.