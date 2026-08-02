# Week 3 Engineering Notes

## MMVP evidence-integrity evaluation

### Models

Small model:
- Model: HuggingFaceTB/SmolVLM-256M-Instruct
- Model revision: main

Larger model:
- Model: Qwen/Qwen2.5-VL-3B-Instruct
- Model revision: main

### Compute

Compute platform:
- Remote GPU environment: gpu048

Runner:
- `src/adapters/run_mmvp_week3.py`

Run date:
- 2026-07-23

### Dataset and manifest

Dataset:
- MMVP

Manifest:
- `data/manifests/week3_mmvp_eval.csv`

Evaluation design:
- 16 MMVP bundles
- 4 evidence conditions per bundle
- 64 rows per model
- 128 total model evaluations

Conditions:
- `image_present`: correct source image provided
- `no_image`: no image provided
- `blank_image`: matched blank white image provided
- `mismatched_image`: image from a different MMVP source provided

Prompt version:
- `mmvp_evidence_integrity_v1`

### Generation parameters

- Temperature: 0.0
- `do_sample`: false
- `max_new_tokens`: 128

### Small-model run

Model:
- `HuggingFaceTB/SmolVLM-256M-Instruct`

Output:
- `outputs/raw/week3_mmvp_small_model.jsonl`

Rows attempted:
- 64

Rows succeeded:
- 64

Rows failed:
- 0

Condition distribution:
- `image_present`: 16
- `no_image`: 16
- `blank_image`: 16
- `mismatched_image`: 16

### Larger-model run

Model:
- `Qwen/Qwen2.5-VL-3B-Instruct`

Output:
- `outputs/raw/week3_mmvp_larger_model.jsonl`

Rows attempted:
- 64

Rows succeeded:
- 64

Rows failed:
- 0

Condition distribution:
- `image_present`: 16
- `no_image`: 16
- `blank_image`: 16
- `mismatched_image`: 16

### Output schema validation

Both model output files were checked for the expected fields:

- `run_id`
- `case_id`
- `bundle_id`
- `source_id`
- `model_name`
- `model_revision`
- `dataset`
- `condition`
- `prompt_version`
- `question`
- `image_path`
- `mismatch_source_id`
- `gold_answer`
- `raw_response`
- `generation_parameters`
- `timestamp`
- `error`

All 128 generated rows were successfully written with no recorded runtime errors.

### Initial response inspection

Sample responses were inspected across all four evidence conditions for both models.

For the `image_present` condition, both models produced responses that generally used the provided image evidence to answer the visual questions.

For the `no_image` condition, the larger model generally recognized that it could not answer image-dependent questions without an image. The smaller model sometimes produced unsupported answers despite receiving no image, demonstrating a potential evidence-integrity failure mode.

For the `blank_image` condition, the larger model generally recognized that the provided image contained no usable visual evidence. The smaller model sometimes generated short answers or unsupported visual claims despite the blank input.

For the `mismatched_image` condition, the larger model often recognized that the provided image did not correspond to the question and explicitly stated that the requested visual evidence was unavailable. The smaller model sometimes produced answers without reliably identifying the mismatch.

These observations are based on initial qualitative inspection of sampled responses and are not intended to replace the formal metric analysis.

### Engineering result

The Week 3 MMVP evidence-integrity runs completed successfully for both model sizes.

The evaluation pipeline successfully executed all four evidence conditions for all 16 MMVP bundles, producing 64 rows per model with zero runtime failures. The resulting outputs preserve the model, revision, prompt version, condition, input-path metadata, generation parameters, raw response, and error fields needed for downstream analysis.

The initial output inspection indicates that model behavior differs across evidence conditions, particularly when the expected visual evidence is absent, blank, or mismatched. The larger model more consistently acknowledged missing or irrelevant visual evidence, while the smaller model showed more cases of answering despite insufficient evidence.

Formal condition-level accuracy and evidence-integrity metrics should be computed separately from these raw outputs.
