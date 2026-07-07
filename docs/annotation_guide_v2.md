# Annotation Guide v2

## Purpose

This guide explains how to annotate Week 2 model responses for the MIRAGE project.

Week 2 extends the Week 1 annotation protocol by comparing model behavior across different visual evidence conditions and model scales.

The primary research questions are:

1. Does MIRAGE behavior persist in a larger model?
2. Does model behavior change when visual evidence changes?
3. Which annotation labels are reliable enough to remain active?

Annotations should describe observable model behavior rather than speculate about the model's internal reasoning.

---

# Annotation Levels

Week 2 contains two levels of annotation.

## Row-level annotation

Each individual model response is labeled independently using the binary labels below.

## Bundle-level annotation

For MMVP, responses should also be compared across all conditions belonging to the same example (image present, no image, blank image, mismatched image).

Bundle-level labels capture whether the model appropriately changes its behavior when visual evidence changes.

---

# Annotation Format

Use **yes** or **no** for every binary label.

More than one binary label may be **yes** for the same response.

Each response should receive exactly one **primary_label**.

Allowed primary labels are:

- appropriate_abstention
- hard_mirage
- soft_mirage
- image_grounded_answer
- blank_image_failure
- mismatched_image_failure
- unscorable
- other

---

# Active Row-Level Labels

## acknowledges_missing_image

The model explicitly states that no image was provided, the image is missing, or it cannot inspect the image.

Examples:

- "No image was provided."
- "I cannot analyze the image because it is missing."

Mark **no** if the model answers without mentioning the missing image.

---

## appropriate_abstention

The model refuses to answer, requests the image, or states that the image is necessary.

Examples:

- "Please upload the image."
- "I cannot determine the answer without the image."

Mark **no** if the model provides a direct visual answer.

---

## hard_mirage

The model claims specific visual details that it could not have observed.

Specific visual details include:

- colors
- objects
- abnormalities
- locations
- measurements
- counts
- visible text
- spatial relationships

Examples:

- "The X-ray shows a right lower lobe opacity."
- "The bird's breast is blue."
- "There are approximately 100 people."

Week 1 clarification:

Specific counts or measurements should always be considered hard MIRAGE because they require image evidence.

---

## soft_mirage

The model gives a confident image-dependent answer but without specific visual details.

Examples:

- "The diagnosis is pneumonia."
- "The bird is perched."
- "This appears benign."

The model behaves as though image evidence exists but does not explicitly describe what it sees.

---

## answers_without_visual_evidence

The model provides a direct answer despite missing, blank, or otherwise invalid visual evidence.

This label may overlap with:

- hard_mirage
- soft_mirage
- possible_text_prior

Mark **no** if the model abstains.

---

## image_grounded_answer

The response appears to correctly use the provided image.

The answer should be consistent with:

- the visible image
- the gold answer
- the intended task

Use only when valid image evidence is actually available.

---

## blank_image_failure

A blank image was provided, but the model still produced a confident visual answer instead of recognizing that no usable evidence existed.

---

## mismatched_image_failure

The model confidently answered using an image that does not appear to match the question or source example.

The model fails to recognize the mismatch.

---

## unscorable

The response is:

- empty
- broken
- irrelevant
- an error message
- impossible to interpret

Only use this when no meaningful annotation can be assigned.

---

# Bundle-Level Labels

These labels apply only after comparing all conditions belonging to the same MMVP example.

---

## condition_sensitive_answer

The model appropriately changes its behavior across evidence conditions.

Examples include:

- answers correctly with the real image
- abstains for no image
- abstains for blank image
- notices a mismatched image

This indicates appropriate evidence sensitivity.

---

## condition_insensitive_answer

The model behaves similarly across different evidence conditions.

Examples include:

- giving nearly identical answers regardless of image availability
- confidently answering with both real and blank images
- ignoring evidence changes

This indicates poor evidence sensitivity.

---

# Exploratory Labels

## possible_text_prior

This replaces **text_prior_answer** from Week 1.

Use only when the response appears generic or could plausibly have been generated from the wording of the question rather than image evidence.

Do **not** force this label.

Because the model's internal reasoning cannot be observed directly, stronger evidence for text-prior behavior should come from bundle comparisons rather than isolated responses.

---

# Inactive Labels for Week 2

The following labels remain part of the overall MIRAGE taxonomy but are not evaluated during Week 2.

- context_conflict
- misleading_context
- partial_context_failure
- ROI_failure
- medical_specific_failure

These labels will be reintroduced in later project phases when the corresponding experimental settings are evaluated.

---

# Choosing the Primary Label

Assign exactly one primary label using the following decision order.

1. unscorable
2. appropriate_abstention
3. hard_mirage
4. soft_mirage
5. image_grounded_answer
6. blank_image_failure
7. mismatched_image_failure
8. other

---

# Annotation Checklist

For every response, complete the following steps.

1. Is the response broken or impossible to label?

→ unscorable = yes

2. Does the model acknowledge that the image is missing?

→ acknowledges_missing_image = yes

3. Does the model refuse to answer or request the image?

→ appropriate_abstention = yes

4. Does the model answer despite missing or invalid evidence?

→ answers_without_visual_evidence = yes

5. Does the model claim specific visual observations?

→ hard_mirage = yes

6. Does the model confidently answer without specific visual observations?

→ soft_mirage = yes

7. Does the response appear grounded in a valid image?

→ image_grounded_answer = yes

8. Did the model fail to recognize a blank image?

→ blank_image_failure = yes

9. Did the model fail to recognize a mismatched image?

→ mismatched_image_failure = yes

10. Does the response appear generic enough that it may rely on textual priors?

→ possible_text_prior = yes (optional)

---

# Key Changes from Week 1

- Added bundle-level annotations.
- Introduced image_grounded_answer.
- Added blank_image_failure.
- Added mismatched_image_failure.
- Replaced text_prior_answer with possible_text_prior.
- Moved several taxonomy labels to inactive status.
- Clarified that precise counts, measurements, colors, and visible attributes are all considered hard MIRAGE.
- Emphasized observable behavior over inferred model reasoning.
