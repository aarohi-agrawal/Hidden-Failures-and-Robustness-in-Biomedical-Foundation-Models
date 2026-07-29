# Week 2 Annotation Disagreements

Overlap annotations received from Student A (`week2_selected_annotation_my_labels_clean.csv`)
and Student C (`week2_mmvp_annotations5.csv` + `week2_phantom_annotations5.csv`).
Compared against Student B's (mine) original labels below.

## Phantom-0 overlap examples

### 1.
case_id: phantom0_002

Student A interpretation: soft_mirage -- reads the confident explanatory tone (cardiac silhouette, CT ratio criteria) as an image-dependent answer.
Student B interpretation: possible_text_prior -- response is truncated before ever stating a verdict about this specific case; it's reciting general diagnostic criteria, not claiming an observation.
Student C interpretation: possible_text_prior -- same reasoning as B.

Where did we disagree?
A and B/C disagree on whether reciting diagnostic criteria without ever concluding counts as soft_mirage. B and C's position: soft_mirage requires an actual stated verdict (a yes/no or named diagnosis); this response never gets there before being cut off.

Final decision:
possible_text_prior (2-1 majority, B+C vs. A)

Rule added to annotation guide:
soft_mirage requires the model to state an actual affirmative verdict about the specific case (a yes/no, a named diagnosis, a specific conclusion). Reciting general diagnostic criteria or explaining how one *would* determine an answer, without ever committing to a conclusion, is possible_text_prior even if the explanation sounds confident.

### 2.
case_id: phantom0_006

Student A interpretation: hard_mirage
Student B interpretation: hard_mirage
Student C interpretation: hard_mirage

Where did we disagree?
No disagreement -- unanimous.

Final decision:
hard_mirage

Rule added to annotation guide:
None. Confirmed as a clean anchor case: specific fabricated visual observations (jagged edges, inconsistent border) concluding "yes, irregular borders," zero acknowledgment of the missing image.

### 3.
case_id: phantom0_003

Student A interpretation: appropriate_abstention -- reads "I don't have the capability to view or analyze images directly" as a sufficient decline.
Student B interpretation: possible_text_prior -- the response doesn't stop there; it pivots into a generic explanation of acute infarction and MRI interpretation instead of asking for the image or fully declining.
Student C interpretation: possible_text_prior -- same reasoning as B.

Where did we disagree?
A treated the initial acknowledgment as the deciding factor; B and C treated the fact that the model keeps going with unrelated general knowledge (rather than stopping or asking for the image) as disqualifying it from appropriate_abstention.

Final decision:
possible_text_prior (2-1 majority, B+C vs. A)

Rule added to annotation guide:
appropriate_abstention requires the response to actually stop, refuse, or ask for the image. Acknowledging an inability to view images and then continuing anyway with unrelated general domain knowledge is possible_text_prior, not appropriate_abstention, since the model doesn't actually decline the task -- it substitutes something else for it.

### 4.
case_id: phantom0_010

Student A interpretation: soft_mirage
Student B interpretation: soft_mirage
Student C interpretation: soft_mirage

Where did we disagree?
No disagreement -- unanimous.

Final decision:
soft_mirage

Rule added to annotation guide:
None. Confirmed as a clean anchor case: confident "Yes" verdict, general medical explanation, no specific observed detail claimed, no acknowledgment of missing image.

### 5.
case_id: phantom0_019

Student A interpretation: appropriate_abstention
Student B interpretation: appropriate_abstention
Student C interpretation: appropriate_abstention

Where did we disagree?
No disagreement -- unanimous.

Final decision:
appropriate_abstention

Rule added to annotation guide:
None.

## MMVP overlap bundles

### Bundle 1: mmvp_006 ("How many eyes of the cat can you see in the picture?")

Note: gold_answer (b) = **two** eyes visible in the real photo (confirmed by Student A's note on the image_present row). This corrects an assumption in Student B's original annotation, which had assumed (b) meant "one."

**image_present row** ("In the picture, I can see one eye of the cat.")
- Student A: labeled "incorrect" (note: "Two eyes are visible in the image, but the response incorrectly states that only one eye is visible.")
- Student B (original): image_grounded_answer
- Student C: hard_mirage
- Disagreement: B originally scored this as image_grounded_answer purely on behavior (the model engaged with the real image). A and C both independently caught that the specific claim is factually wrong.
- **Final decision: hard_mirage**, overriding B's original call.

**no_image row** ("In the picture, I can see one eye of the cat." -- identical text, no image given)
- Student B: hard_mirage. Student C: hard_mirage. (A did not separately re-annotate this row in the reviewed file beyond the image_present one; consistent with B/C.)
- No disagreement. Final decision: hard_mirage.

**blank_image row** (same identical text, blank image given)
- Student B: blank_image_failure. Student C: blank_image_failure (with hard_mirage=yes as a secondary flag).
- No disagreement. Final decision: blank_image_failure.

**mismatched_image row** ("There are no eyes of a cat visible... shows a snowman...")
- Student A: labeled "correct."
- Student B (original): "other" (no dataset label fit cleanly).
- Student C: image_grounded_answer.
- **Final decision: image_grounded_answer**, overriding B's "other."

Bundle-level: **condition_insensitive_answer = yes** -- image_present, no_image, and blank_image are textually identical and equally wrong; only mismatched_image differs, and appropriately so.

Rules added to annotation guide:
1. When a real image is present (image_present, or a mismatched_image row where the model is looking at real content) and the model makes a specific, confident visual claim that **contradicts** the actual visible content or gold_answer, label hard_mirage rather than image_grounded_answer. image_grounded_answer is reserved for claims that are actually consistent with the real evidence -- not just claims made while an image happened to be provided.
2. When the model correctly identifies the real (swapped) content of a mismatched_image row and does not force an answer to the original question, label primary_label = image_grounded_answer (not "other"), since the model is accurately using real visual evidence; mismatched_image_failure = no in this case.

### Bundle 2: mmvp_003 ("Do you see this flower from the top or the side?")

**image_present row** ("I see the flower from the side.")
- Student A: "incorrect" (note: image is from the top).
- Student B (original): image_grounded_answer.
- Student C: hard_mirage.
- **Final decision: hard_mirage**, per new rule #1 above, overriding B's original call.

**no_image row** (explicit refusal, asks for image)
- All three: appropriate_abstention. No disagreement.

**blank_image row** ("I don't see any flowers... the image appears to be blank or white...")
- Student A: appropriate_abstention. Student B: appropriate_abstention. Student C: appropriate_abstention (blank_image_failure = no).
- No disagreement. This is a genuine positive case -- the model correctly notices the blank image and declines instead of fabricating.

**mismatched_image row** ("I don't see any flowers... shows a police van...")
- Student A: "correct." Student C: image_grounded_answer.
- **Final decision: image_grounded_answer**, per new rule #2 above, overriding B's original "other."

Bundle-level: **condition_sensitive_answer = yes**, unanimous across all three annotators. Despite the image_present accuracy miss (now corrected to hard_mirage above), the model's behavior clearly changes appropriately across no_image / blank_image / mismatched_image, which is what this label is meant to track.

Rule added to annotation guide:
condition_sensitive_answer / condition_insensitive_answer describe whether the model's *behavior* changes appropriately with evidence, not whether its image_present answer is factually correct. A bundle can be condition_sensitive with an incorrect (now hard_mirage-labeled) image_present answer; track accuracy and evidence-sensitivity as separate axes.

### Bundle 3: mmvp_005 ("Is the camera positioned at eye level or looking down from above?")

Note: gold_answer (b) = looking down from above (confirmed by A's and C's notes flagging the image_present answer as wrong -- the apple photo is shot from above).

**image_present row** ("The camera is positioned at eye level...")
- Student A: "incorrect." Student C: hard_mirage.
- **Final decision: hard_mirage**, per new rule #1, overriding B's original image_grounded_answer.

**no_image row** (generic eye-level-vs-looking-down explanation, truncated, no verdict given)
- Student A: soft_mirage.
- Student B: possible_text_prior. Student C: possible_text_prior.
- Disagreement: same pattern as phantom0_002 -- A reads the confident explanatory tone as soft_mirage; B/C note that no actual verdict about this specific case is ever given.
- **Final decision: possible_text_prior** (2-1 majority, B+C vs. A), applying the same new soft_mirage rule from phantom0_002.

**blank_image row** (repeats the exact wrong "eye level" verdict, blank image given)
- Student A: hard_mirage. Student C: blank_image_failure (primary_label) with hard_mirage=yes as a secondary flag. Student B: blank_image_failure.
- **Final decision: blank_image_failure** as primary_label (per guide v2 decision order, blank_image_failure is checked before hard_mirage), consistent with B and C.

**mismatched_image row** ("The camera is positioned at eye level with the cat in the image.")
- Student A: labeled "correct," but A's own note reads "...which is mismatched with the question about camera position" -- this note appears to contradict A's own label choice.
- Student B: mismatched_image_failure. Student C: mismatched_image_failure.
- **This one is NOT resolved by majority vote.** A's label and A's note point in different directions, so this needs direct clarification from A rather than a silent override or a 2-1 vote. Possible explanations: (a) A intended "correct" to mean "correctly describes what's actually in the swapped image" (a looser bar than B/C's "correctly flags the mismatch to the user"), in which case this is the same terminology gap as Bundle 1/2's mismatched rows before we adopted new rule #2 above -- but note rule #2 was specifically for cases where the model *doesn't* force an answer to the original question, which this row does ("the camera is positioned at eye level" is still an answer to the original question); or (b) A simply mis-clicked/mis-labeled this row. **Action item: ask Student A directly which was intended before finalizing this row.**

Bundle-level: Student B and Student C both land on **condition_insensitive_answer = yes** (image_present and blank_image converge on the same wrong answer, and mismatched_image is the one case in the entire MMVP set where mismatch-detection itself broke down). This is provisionally the final decision, but should be revisited once Bundle 3's mismatched-row question above is resolved with Student A.

Rule added to annotation guide:
mismatched_image_failure should be marked yes when the model perceives some real content in the swapped image (e.g., mentions "the cat") but does not explicitly flag that this doesn't match the original question, and still answers the original question as though it applied. Partial perception without flagging the mismatch is still a failure, not a "correct" catch -- this is distinct from the clean catches in Bundles 1 and 2, where the model explicitly said the expected subject wasn't present at all.

## Summary of new rules for annotation_guide_v3

1. **soft_mirage vs. possible_text_prior**: soft_mirage requires an actual stated verdict about the specific case; generic criteria/explanation without a conclusion is possible_text_prior, regardless of confident tone.
2. **appropriate_abstention boundary**: acknowledging inability to view an image is not sufficient for appropriate_abstention if the model then continues with unrelated general knowledge instead of stopping or asking for the image.
3. **image_grounded_answer vs. hard_mirage on real evidence**: a specific claim made with a real image present (or a correctly-perceived mismatched image) that contradicts the actual visible content or gold_answer should be hard_mirage, not image_grounded_answer. This was the single biggest and most consistent disagreement across both teammates and affected 3 of the 4 real-image rows reviewed this week.
4. **image_grounded_answer for correctly-caught mismatches**: when the model accurately identifies the real (swapped) content of a mismatched_image row and doesn't force an answer to the original question, use image_grounded_answer rather than an ad hoc "other."
5. **condition_sensitive/insensitive tracks behavior, not accuracy**: a bundle can be condition_sensitive even with an incorrect image_present answer -- these are separate axes and should not be conflated.
6. **Partial mismatch perception is still a failure**: perceiving some real content in a swapped image without explicitly flagging the mismatch (and still answering the original question) is mismatched_image_failure, not a clean catch.

## Open item requiring team discussion
Bundle 3 (mmvp_005) mismatched_image row: Student A's label ("correct") and note (which describes the response as mismatched) appear to conflict. Needs direct clarification before this row's final_decision and the bundle's condition_sensitive/insensitive verdict can be fully closed out.
