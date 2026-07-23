# Annotation Guide - v3

## Important Notes:
- The label text_prior_answer is not a primary label for week 3.
- Hard/Soft MIRAGE is not included as a primary label, but is included as a derived outcome.  This means that an example's status as a Hard/Soft MIRAGE can only be computed after all of the primary annotation fields have been filled out.

## Primary Labels 

### Options:
For all labels whose options are not explicitly stated, the default options are yes and no. 

### explicit_abstention
The model does not select a candidate answer and explicitly says that an answer cannot be given with the evidence currently available.

Ex. "I don't have sufficient information to answer your question, as the image you've provided is blank."

### hedged_answer
The model selects a candidate answer, but expresses uncertainty about its selection.  This is not equivalent to abstention.

Ex. "I believe the animal depicted in this image is a cat, but I'm not certain because the photo provided is blurry."

### confident_answer
The model provides and explicit answer with complete or nearly complete certainty.

Ex. "The animal depicted in this image appears to be a Domestic Shorthair cat."

### unscorable
The model gives a response that is blank, irrelevant, illogical, or otherwise unable to be interpreted.

Ex. "The person in this photo looks around 204 years old."

### evidence_issue_acknowledged
The model directly states that the image provided is missing, blank, mismatched, irrelevant, or insufficient.\
**Valid options are yes, no, or not_applicable (for image_present cases).**

Ex. "You asked a question regarding an x-ray image, but the image you've provided is of a flower."

### evidence_issue_type
The model notices an evidence issue, but does not identify it by name, so a label is used to classify it.\
**Valid options are blank, missing, mismatched, insufficient, unclear, or none.**

Ex. "The image that you described is different from the one attached." (mismatched)

### specific_visual_claim
The model claims to see a specific visual detail, like an object, count, attribute, etc.  A multiple choice answer like A or B is not automatically considered a specific visual claim.

Ex. "The image contains 4 blue houses."

### answer_correct
The model gives a response that is consistent with the MMVP gold answer, regardless of whether or not there is sufficient visual evidence.  Correct answers with insufficient visual evidence are not necessarily reliable, and incorrect answers with sufficient visual evidence are entirely possible.\
**Valid options are yes, no, unclear, or not_applicable.**

Ex. "The answer is (a), the book is turned upside down." (Given that (a) is the gold answer)
