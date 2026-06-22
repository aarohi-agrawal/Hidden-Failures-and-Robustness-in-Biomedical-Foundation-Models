# Week 0 Engineering Notes

## What I tried

Created the project repository structure, environment file, configuration file, and Hugging Face VLM smoke-test adapter.

Commands used:

```bash
pip install -r requirements.txt

python -c "import torch, transformers, pandas, PIL, yaml; print('environment works')"

python src/adapters/hf_vlm_smoke_test.py
```

## Did the environment install?

Yes

## Did the VLM load?

Partially. The script executed and generated an output file, but the model inference step failed due to an unsupported Hugging Face pipeline task.

## CPU or GPU?

CPU

## What image did I use?

Image source:

Public image from the Hugging Face documentation tutorial.

## What question did I ask?

Question:

Describe this image in one sentence.

## What output file was written?

Path:

outputs/raw/week0_vlm_smoke_test.jsonl

## If something failed, what was the error?

The smoke-test script successfully executed and wrote an output file, but the VLM inference failed with the following error:

```text
Unknown task image-to-text, available tasks are
['any-to-any', 'audio-classification',
'automatic-speech-recognition',
'depth-estimation',
'document-question-answering',
'feature-extraction',
'fill-mask',
'image-classification',
'image-feature-extraction',
'image-segmentation',
'image-text-to-text',
'keypoint-matching',
'mask-generation',
'ner',
'object-detection',
'sentiment-analysis',
'table-question-answering',
'text-classification',
'text-generation',
'text-to-audio',
'text-to-speech',
'token-classification',
'video-classification',
'zero-shot-audio-classification',
'zero-shot-classification',
'zero-shot-image-classification',
'zero-shot-object-detection']
```

The output file was still generated because the exception was captured and written to the JSONL output.

## What should we fix before Week 1?

1. Update the Hugging Face pipeline implementation to use the correct task type for SmolVLM.
2. Verify successful image loading and response generation from the model.
3. Validate the output schema against future benchmark requirements.
4. Test the pipeline on additional image-question pairs before beginning benchmark construction.
