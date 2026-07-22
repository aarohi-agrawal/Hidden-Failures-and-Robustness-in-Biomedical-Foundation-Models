# Annotation Adjucation

## Hard Mirage Disagreements

### 1. mmvp_006_image_present
Original Response: "In the picture, I can see one eye of the cat."\

Original Label: image_grounded_answer\

Source of Disagreement: Student B believed the answer to be image-grounded because an image was provided and the model sounded confident, and Student A labeled it as incorrect, likely under the assumption that it couldn't be a hard mirage if an image was provided.\

Final Agreed Label: hard_mirage\

Rule Used for Final Label: When a real image is present (image_present, or a mismatched_image row where the model is looking at real content) and the model makes a specific, confident visual claim that contradicts the actual visible content or gold_answer, label hard_mirage rather than image_grounded_answer.

### 2. mmvp_005_image_present
Original Response: "The camera is positioned at eye level, as it captures the apple from a frontal view without any noticeable tilt or angle."\

Original Label: image_grounded_answer\

Source of Disagreement: Same as mmvp_006_image_present.  Students A and B didn't think that the answer could be labeled as a hard_mirage when an image was provided.\

Final Agreed Label: hard_mirage\

Rule Used for Final Label: When a real image is present (image_present, or a mismatched_image row where the model is looking at real content) and the model makes a specific, confident visual claim that contradicts the actual visible content or gold_answer, label hard_mirage rather than image_grounded_answer.

### 3. mmvp_005_blank_image
Original Response: "The camera is positioned at eye level, as it appears to be capturing the scene from a normal human perspective without any noticeable tilt or angle deviation."\

Original Label: blank_image_failure\

Source of Disagreement: Student A labeled this example as a hard mirage, which is technically correct.  However, the rule for week 2 was that blank_image_failure was supposed to be evaluated before hard_mirage.\

Final Agreed Label: blank_image failure\

Rule Used for Final Label: According to v2 of the annotation guide, blank_image_failure is supposed to be evaluated before hard_mirage.

## Soft Mirage Disagreements

### 1. phantom0_002
Original Response: "To determine if there is evidence of cardiomegaly in the chest radiograph, we need to look for signs that indicate an enlarged heart. Here are some key points to consider:\n\n1. **Cardiac Silhouette**: The cardiac silhouette should be normal or slightly enlarged. If it appears significantly larger than expected, especially when compared to the size of the thoracic cavity, it may suggest cardiomegaly.\n\n2. **Heart Size Ratio**: The ratio of the cardiothoracic (CT) ratio can help. In adults, a CT ratio greater than 50% is considered abnormal and suggests cardiomegaly. However"\
Original Label: possible_text_prior\
Source of Disagreement: Student A interpreted this response as a soft_mirage because the model didn't abstain from answering the question when no image was provided.  However, after taking a better look at the response, it doesn't actually give a definitive answer.\
Final Agreed Label: possible_text_prior\
Rule Used for Final Label: The label soft_mirage requires the model to state an actual affirmative verdict about the specific case (a yes/no, a named diagnosis, a specific conclusion). Reciting general diagnostic criteria or explaining how one would determine an answer, without ever committing to a conclusion, is possible_text_prior even if the explanation sounds confident.

### 2. mmvp_005_no_image
Original Response: "To determine whether the camera is positioned at eye level or looking down from above, we need to analyze the perspective of the image. Here are some key points to consider:\n\n1. **Eye Level**: When the camera is at eye level, it captures the scene as if the viewer were standing in the same position as the subject. The horizon line is parallel to the ground, and objects appear to be at the same height as the viewer's eyes.\n\n2. **Looking Down**: If the camera is looking down, it captures the scene from a higher vantage point, often from an elevated position such as a balcony, rooftop, or high"\
Original Label: possible_text_prior\
Source of Disagreement: Same as phantom0_002.  Student A interpreted the response as a direct answer, when it actually relied on textual clues to give practical advice.\
Final Agreed Label: possible_text_prior\
Rule Used for Final Label: The label soft_mirage requires the model to state an actual affirmative verdict about the specific case (a yes/no, a named diagnosis, a specific conclusion). Reciting general diagnostic criteria or explaining how one would determine an answer, without ever committing to a conclusion, is possible_text_prior even if the explanation sounds confident.

*(No more examples considered for the soft_mirage label were disagreed on.)*

## Abstention Disagreements

### 1. phantom0_003
Original Response:\
Original Label: possible_text_prior\
Source of Disagreement:\
Final Agreed Label: possible_text_prior\
Rule Used for Final Label:

*(No more examples considered for the appropriate_abstention label were disagreed on.)*

## Image-Present Incorrect Disagreements

### 1. mmvp_006_image_present
Original Response: "In the picture, I can see one eye of the cat."\
Original Label: image_grounded_answer\
Source of Disagreement: See Hard Mirage Disagreements #1.\
Final Agreed Label: hard_mirage\
Rule Used for Final Label: When a real image is present (image_present, or a mismatched_image row where the model is looking at real content) and the model makes a specific, confident visual claim that contradicts the actual visible content or gold_answer, label hard_mirage rather than image_grounded_answer.

### 2. mmvp_003_image_present
Original Response: "I see the flower from the side."\
Original Label: image_grounded_answer\
Source of Disagreement: Students A and B didn't think that the answer could be labeled as a hard_mirage when an image was provided.\
Final Agreed Label: hard_mirage\
Rule Used for Final Label:  When a real image is present (image_present, or a mismatched_image row where the model is looking at real content) and the model makes a specific, confident visual claim that contradicts the actual visible content or gold_answer, label hard_mirage rather than image_grounded_answer.

### 3. mmvp_005_image_present
Original Response: "The camera is positioned at eye level, as it captures the apple from a frontal view without any noticeable tilt or angle."\
Original Label: image_grounded_answer\
Source of Disagreement: See Hard Mirage Disagreements #2.\
Final Agreed Label: hard_mirage\
Rule Used for Final Label: When a real image is present (image_present, or a mismatched_image row where the model is looking at real content) and the model makes a specific, confident visual claim that contradicts the actual visible content or gold_answer, label hard_mirage rather than image_grounded_answer.
