# Week 3 - Annotation Disagreements

## Disagreement #1
Bundle ID: mmvp_w3_002
Model: HuggingFaceTB/SmolVLM-256M-Instruct
Condition: image_present

Field Disagreement: answer_correct

Student A's Answer: no (answer did not align with gold answer)
Student B's Answer: yes (likely based on personal interpretation, rather than gold answer)
Student C's Answer: no (answer did not align with gold answer)

Final Decision: answer_correct -> no
Rule Used: In order for an answer to be correct, the model must give a response that is consistent with the official MMVP gold answer.

## Disagreement #2
Bundle ID: mmvp_w3_008
Model: HuggingFaceTB/SmolVLM-256M-Instruct
Condition: image_present

Field Disagreement: specific_visual_claim

Student A's Answer: no (answer was specific, but did not directly describe the details of the image)
Student B's Answer: no (answer was specific, but did not directly describe the details of the image)
Student C's Answer: yes (did not account for answer's lack of visual contect)

Final Decision: specific_visual_claim -> no
Rule Used: A multiple choice answer (like upside-down or upright) is not automatically considered to be a specific visual claim.  In this case, the model simply selected an option, without providing an actual description of what was going on in the image.