# Annotation Guide v1

## Purpose

This guide defines how to label model responses for the Week 1 Phantom-0 no-image evaluation.

The Week 1 research question is:

When a model receives a visual question without an image, does it recognize that the image is missing, or does it answer as if it saw the image?

These annotations describe model behavior. They are not meant to judge whether the model’s answer is medically or visually correct, because no image evidence was provided.

## Annotation Format

The binary label columns should be marked with yes or no.

The binary labels are multi-label. This means more than one label can be marked yes for the same response.

For example, this response:

"I cannot answer because no image was provided."

would receive:

acknowledges_missing_image: yes

appropriate_abstention: yes

The primary_label should capture the most important behavior in the response.

Allowed primary_label values:

appropriate_abstention

hard_mirage

soft_mirage

text_prior_answer

unscorable

other

## Annotation Decision Checklist

For each response, apply the labels by checking whether the response:

1. explicitly acknowledges that no image was provided;
2. refuses to answer or asks for the image;
3. gives a direct answer despite missing image evidence;
4. describes specific visual details;
5. appears to reason from text clues or general knowledge;
6. is broken, irrelevant, empty, or impossible to label.