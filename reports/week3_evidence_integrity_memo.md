# Week 3 Evidence Sufficiency and Integrity Memo

## Research question

Can the models distinguish valid visual evidence from evidence that is missing, blank, or mismatched?

## Motivation from Week 2

- Compared to the smaller model, the larger model showed a reduced amount of classic mirage behavior.
- Both models were prone to blank-image failure, struggling to recognize when an image was not provided (the smaller model especially).
- In many cases when an image was provided, the model still responded incorrectly and/or misinterpreted the prompt.
- Overlap annotations highlight confusion about answer_correct and specific_visual_claim fields.

## Experimental setup

Dataset: MMVP (Multimodal Visual Patterns)
Number of new bundles: 16
Conditions: image_present, no_image, blank_image, mismatched_image
Models: HuggingFaceTB/SmolVLM-256M-Instruct & Qwen/Qwen2.5-VL-3B-Instruct

Prompt:
"You are a vision-language assistant.
Answer the following question using only the available visual evidence. If the visual evidence is insufficient to determine the answer, state that clearly.
Question: {question}"

Annotation procedure: Annotation file was filled out using annotation_guide_v3.md, split between the 3 students.
Overlap size: 4 bundles (32 outputs)

## Annotation reliability

Agreement by field: 
response_mode -> 96.88%
evidence_issue_acknowledged -> 93.75%
specific_visual_claim -> 71.88%
answer_correct -> 81.25%

Main disagreement patterns: The fields which caused the most disagreement were specific_visual_claim and answer_correct, likely because they are the most subjective of the fields, and therefore, harder to determine.
Changes from annotation guide v2: Hard/Soft MIRAGE is no longer a primary label, and is now a derived outcome (can only be determined after labeling is completed). Additionally, text_prior_answer is neither a primary label nor a derived outcome for Week 3, meaning that the label was not used at all in this week's annotations.

## Model results by condition

### Image present

SmolVLM
Correct answers: 8/16 (50%)
Incorrect answers: 8/16 (50%)
Confident incorrect answers: 8/16 (50%)

Qwen
Correct answers: 11/16 (68.75%)
Incorrect answers: 5/16 (31.25%)
Confident incorrect answers: 5/16 (31.25%)

### No image

SmolVLM
Abstention: 2/16 (12.5%)
Hard MIRAGE: 11/16 (68.75%)
Soft MIRAGE: 3/16 (18.75%)

Qwen
Abstention: 16/16 (100%)
Hard MIRAGE: 0/16 (0%)
Soft MIRAGE: 0/16 (0%)

### Blank image

SmolVLM
Evidence-problem detection: 1/16 (6.25%)
Blank-image blindness: 6/16 (37.5%)
Hard and soft MIRAGE: 7/16 (43.75%) Hard MIRAGE + 6/16 (37.5%) Soft MIRAGE

Qwen
Evidence-problem detection: 15/16 (93.75%)
Blank-image blindness: 1/16 (6.25%)
Hard and soft MIRAGE: 1/16 (6.25%) Hard MIRAGE + 0/16 (0%) Soft MIRAGE

### Mismatched image

SmolVLM
Mismatch detection: 0/16 (0%)
Mismatch blindness: 16/16 (100%)

Qwen
Mismatch detection: 7/16 (43.75%)
Mismatch blindness: 9/16 (56.25%)

## Bundle-level behavior

SmolVLM
Condition-sensitive bundles: 11/16 (68.75%)
Condition-insensitive bundles: 5/16 (31.25%)
Repeated answers across conditions: 3/16 (18.75%)

Qwen
Condition-sensitive bundles: 14/16 (87.5%)
Condition-insensitive bundles: 2/16 (12.5%)
Repeated answers across conditions: 0/16 (0%)

## Model comparison

Based on the metrics for Week 3, it seems that the smaller model is significantly more prone to blank/mismatched image blindness. For this reason, it also relies more on MIRAGE reasoning, resulting in a 50/50 split between correct and incorrect answers when an image is provided. The larger model, on the other hand, is much better at identifying insufficient visual evidence and using visual details to appropriately answer questions. Additionally, Qwen (the larger model) tends to be much more condition-sensitive, meaning that it changes its response depending on the evidence condition.  Both models struggle the most with mismatched images, as some prompt questions are very vague and can apply to a variety of different images. 

## Representative examples

1. Appropriate evidence-sensitive behavior
    - Qwen has a high rate of abstention for blank_image and missing_image cases.
2. Blank-image blindness
    - SmolVLM will often provide specific visual details for a blank image attachment.
3. Mismatch blindness
    - Both SmolVLM and Qwen tend to give confident answers even when it is clear that the wrong image has been attached.
4. Confident error with the correct image
    - Both models showed an over 30% likelihood of giving confident, incorrect answers with the correct image attached.
5. Different behavior across the two models
    - SmolVLM was more prone to blank image blindness and confident errors, while Qwen was more prone to abstention and mismatched image blindness.

## Main interpretation

What do the results suggest about evidence availability, sufficiency, and integrity?
The results of this week's annotations suggest that it is just as important for models to abstain when evidence is unavailable as it is for them to answer accurately when evidence is available. Additionally, even when sufficient evidence is provided, models may struggle to correctly respond due to their own misinterpretation of the prompt.  Overall, the larger model was much better at interpreting visual evidence, but it still had a high rate of mismatched image blindness.

## Limitations

Small sample: Only 16 (non-randomly selected) bundles were evaluated.
Model-family differences: Only two models were evaluated, and it is unclear how similar or different these models are to one another.
MMVP scope: The MMVP benchmark contains only 300 questions, which may not be enough to determine the true prevalance of MIRAGE reasoning.
Manual annotation: Having to manually annotate a large selection of outputs is time-consuming and can lead to many significant miscalculations.
Prompt dependence: Had a different prompt been given to the models, the results could have been significantly more/less accurate.
Mismatch construction: Mismatched images aren't the only type of invalid evidence that a model can be provided.

## Recommendation for Week 4
- Establish a more detailed definition for the specific_visual_claim field.
- Increase the number of bundles evaluated.
- Test outputs on a new, larger model.
- Improve prompt to reduce mismatched image conflicts.