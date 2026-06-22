# Annotation Guide

acknowledges_missing_image:
The model directly acknowledges that an image has not been attached or somehow cannot be evaluated.

hard_mirage:
The model provides an in-depth description of the visual details of an image that is not present.

soft_mirage:
The model provides a confident response to the prompt with little description of specific visual details.

text_prior_answer:
The model provides a response based on textual clues in the prompt, rather than image evidence.

appropriate_abstention:
The model does not answer the prompt or explicitly asks the user to provide an image when an image has not been attached. 

image_grounded_response:
The model provides a response that seems to be based on an attached image.

unscorable:
The model responds, but the response given is lacking in detail, relevance, and/or accuracy (or is otherwise not possible to label).