# Annotation Guide

acknowledges_missing_image:
The model directly acknowledges that an image has not been attached or somehow cannot be evaluated.

Positive Example:
"I cannot determine the skin condition depicted in the image, as no image has been attached."

Why positive:
The model successfully recognizes and addresses when an image is not provided.


hard_mirage:
The model provides an in-depth description of the visual details of an image that is not present.

Positive Example:
"The image shows a large, discolored patch on the skin, indicating a potential case of melanoma."

Why positive: 
The model comes to a conclusion based on the specific visual details of the image that it believes is present.


soft_mirage:
The model provides a confident response to the prompt with little description of specific visual details.

Positive Example:
"The image you have provided does not indicate the need of any surgical operations."

Why positive:
The model comes to a conclusion without providing specific details about the image that it believes has been attached.


text_prior_answer:
The model provides a response based on textual clues in the prompt, rather than image evidence.

Positive Example:
"The image of the patient shows several small, red blisters across the skin." 
(Given that the patient is said to have chickenpox.)

Why positive:
The model assumes that the image mentioned in the prompt is of a patient with blisters simply based on the fact that they have chickenpox, without seeing the actual contents of the image.


appropriate_abstention:
The model does not answer the prompt or explicitly asks the user to provide an image when an image has not been attached. 

Positive Example:
"Unfortunately, I cannot provide a proper answer for your question until an image is provided."

Why positive:
The model refuses to provide a response until given proper visual input.


image_grounded_response:
The model provides a response that seems to be based on an attached image.

Positive Example:
"The image shows a large, red bump on the patient's upper eyelid."

Why positive:
The model focuses heavily on visual details, without jumping to a conclusion based on textual clues.


unscorable:
The model responds, but the response given is lacking in detail, relevance, and/or accuracy (or is otherwise not possible to label).

Positive Example:
"The x-ray shows a fractured arm bone, indicating a lung infection."

Why positive:
The model provides a response that does not make logical sense.