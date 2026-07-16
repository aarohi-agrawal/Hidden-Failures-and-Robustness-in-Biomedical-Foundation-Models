# Week 2 Combined Memo

## Research questions
1. Does MIRAGE behavior persist in a larger model?
2. Does the model behave differently when visual evidence is present, missing, blank, or mismatched?
3. Which labels are reliable enough to keep active?

## Setup
Phantom-0 examples: 40 (20 implicit_no_image + 20 explicit_missing_image, same case_ids as Week 1)
Phantom-0 model: Qwen/Qwen2.5-VL-3B-Instruct
MMVP bundles: 8 (mmvp_001 - mmvp_008), 32 total rows across 4 conditions each
MMVP model: Qwen/Qwen2.5-VL-3B-Instruct
Conditions: Phantom-0 tested no_image only (implicit and explicit prompt variants); MMVP tested all four: image_present, no_image, blank_image, and mismatched_image (round-robin swapped real images between bundles)
Date run: 2026-07-08 (Phantom-0) / 2026-07-11 (MMVP), per raw output timestamps
Overlap annotation: 5 Phantom-0 outputs + 3 MMVP bundles independently labeled by Student A and Student C; results below reflect the corrected labels after that review (see `docs/week2_annotation_disagreements.md` for full reasoning)

## Phantom-0 larger-model results
Appropriate abstention: 33 / 40 (82.5%)
Hard MIRAGE: 1 / 40 (2.5%)
Soft MIRAGE: 2 / 40 (5%)
Answers without visual evidence: 7 / 40 (17.5%)
Possible text prior: 4 / 40 (10%) -- overlaps with the 7 "answers without visual evidence" rows above, not additive
Comparison to Week 1 small model (SmolVLM-256M-Instruct):

| metric | Week 1 (SmolVLM-256M) | Week 2 (Qwen2.5-VL-3B) |
|---|---|---|
| appropriate_abstention_count | 2 / 40 (5%) | 33 / 40 (82.5%) |
| hard_mirage_count | 25 / 40 (62.5%) | 1 / 40 (2.5%) |
| soft_mirage_count | 12 / 40 (30%) | 2 / 40 (5%) |
| answers_without_visual_evidence_count | 38 / 40 (95%) | 7 / 40 (17.5%) |
| text_prior_answer / possible_text_prior count | 1 / 40 (2.5%) | 4 / 40 (10%) |
| acknowledges_missing_image_count | 2 / 40 (5%) | 35 / 40 (87.5%) |

The larger model shows a dramatic reduction in MIRAGE behavior on Phantom-0: it explicitly acknowledges the missing image in the large majority of cases (35/40) and abstains appropriately far more often (33/40 vs. 2/40 for the small model). Hard MIRAGE, which was the dominant behavior for the small model (25/40), nearly disappears (1/40).

All 5 Phantom-0 overlap examples were independently reviewed by Student A and Student C. Three were unanimous across all three annotators (phantom0_006 = hard_mirage, phantom0_010 = soft_mirage, phantom0_019 = appropriate_abstention). The other two (phantom0_002, phantom0_003) split 2-1, with Student A reading a confident explanatory tone as soft_mirage/appropriate_abstention while Student B and Student C read the lack of any actual stated verdict as possible_text_prior. Majority decision both times was possible_text_prior, which matched Student B's original labels -- no corrections were needed to the Phantom-0 annotation file as a result of overlap review.

## MMVP paired-evidence results
Image-present grounded/correct responses: 5 / 8 (62.5%) -- **revised down from an initial 8/8** after overlap review. Student A and Student C both independently caught that 3 of the 8 image_present responses make a specific, confident claim that contradicts the actual visible content or gold_answer (mmvp_003: says "side" when the real photo is from the top; mmvp_005: says "eye level" when the real photo is shot looking down; mmvp_006: says "one eye" when the real photo shows two). These 3 rows were relabeled hard_mirage, since a specific fabricated-and-wrong visual claim is still a fabrication even when a real image was technically provided -- see "Label validation" below for the new rule this produced.
No-image answer-without-evidence responses: 2 / 8 (25%) -- 5/8 abstain appropriately, 2/8 fabricate a specific hard_mirage answer (mmvp_001, mmvp_006), 1/8 gives a non-committal generic explanation without concluding (possible_text_prior, mmvp_005).
Blank-image failures: 7 / 8 (87.5%) -- the model confidently answers as if it had real evidence in almost every blank-image case. Only 1/8 (mmvp_003) correctly notices the image is blank and declines.
Mismatched-image failures: 1 / 8 (12.5%) -- the model correctly notices and flags 7 of 8 image/question mismatches, describing the actual (wrong) image content instead of forcing an answer to the original question. These 7 were relabeled from an ad hoc "other" to image_grounded_answer after overlap review, since the model is genuinely using real visual evidence accurately, just evidence that reveals the question doesn't apply. Only mmvp_005 fails to flag the swap -- notably the same bundle whose image_present and blank_image responses were also wrong, making mmvp_005 the single weakest bundle in the dataset across every condition.
Condition-sensitive bundles: 6 / 8 (mmvp_001, mmvp_002, mmvp_003, mmvp_004, mmvp_007, mmvp_008) -- these bundles show at least some evidence-appropriate behavior change, most consistently abstaining under no_image and correctly catching mismatched_image, even when blank_image handling is imperfect and/or the image_present answer itself is wrong (an accuracy issue tracked separately from evidence-sensitivity per the overlap review).
Condition-insensitive bundles: 2 / 8 (mmvp_005, mmvp_006) -- these two bundles give the same or near-same answer regardless of what evidence is actually provided; mmvp_006 is the cleanest case (identical text across image_present/no_image/blank_image) and mmvp_005 is the most concerning (also fails to catch the mismatched-image swap -- flagged as an open item pending clarification with Student A, see disagreements doc).

A pattern worth highlighting: **blank_image is by far the weakest condition** (7/8 failures) while **mismatched_image is by far the strongest** (7/8 correctly caught, once corrected). This suggests the model's grounding failure is specifically about *recognizing the absence of usable visual content* (a blank canvas), not about visual processing in general -- when the swapped image actually contains something (a snowman, a shark, an apple), the model reliably describes what's really there instead of answering the original question; but when there's nothing to see, it falls back to a default guess instead of recognizing that there's nothing to describe.

A second pattern that only emerged after overlap review: **the model can fabricate specific wrong visual details even with a real image present.** 3 of 8 image_present responses (37.5%) contain a confident, specific claim that simply doesn't match the real photo. This means "image was provided" is not the same as "image was actually used correctly" -- a distinction the original annotation (image_grounded_answer for any image_present row) missed, and one that both teammates independently caught.

## Label validation
Labels that worked well: `acknowledges_missing_image` and `appropriate_abstention` remained unambiguous on Phantom-0, exactly as in Week 1 -- the larger model's refusals are almost always explicit ("I cannot... as there is no image provided"), making these two labels trivial to apply consistently, and all 3 unanimous Phantom-0 overlap examples used these labels. On MMVP, `blank_image_failure` was easy and highly reliable (7/8, unanimous wherever compared) and, after correction, `image_grounded_answer` for mismatched_image rows was also unanimous across all three annotators once the "other" placeholder was retired.

Labels that were confusing: Two distinct confusions emerged from overlap review, both substantial enough to change the annotation file:
1. **soft_mirage / appropriate_abstention vs. possible_text_prior**: on both phantom0_002 and phantom0_003 (Phantom-0) and mmvp_005's no_image row (MMVP), Student A read a confident-sounding explanation of general criteria as soft_mirage or appropriate_abstention, while Student B and Student C read the *absence of any actual verdict about the specific case* as possible_text_prior. This was a consistent 2-1 pattern, not a one-off.
2. **image_grounded_answer vs. hard_mirage when a real image is present but the claim is wrong**: this was the single biggest disagreement of the week, affecting 3 of 8 MMVP image_present rows. Student B's original approach scored these behaviorally (the model engaged with a real image, therefore "grounded"); both teammates independently scored them on accuracy (the specific claim is factually wrong, therefore MIRAGE-like even with real evidence present). The team adopted the accuracy-sensitive version.

Labels moved to exploratory: `text_prior_answer` (Week 1) was already replaced by `possible_text_prior` per the Week 2 guide before annotation began, exactly because Week 1 showed it rarely fired (1/40) and overlapped awkwardly with hard/soft mirage. This week's Phantom-0 data reinforces that decision: `possible_text_prior` fired more often (4/40) but always as a secondary/tie-breaking judgment, and 2 of the 5 overlap-reviewed Phantom-0 examples were exactly this kind of borderline call -- both resolved in favor of possible_text_prior by majority vote.

Labels inactive until later: `context_conflict`, `misleading_context`, `partial_context_failure`, `ROI_failure`, `medical_specific_failure` remain untested this week. Worth deciding in Week 3 whether `context_conflict` should eventually be merged with or kept distinct from `mismatched_image_failure`, which turned out to need its own nuance this week (see next point).

New labels/rules to carry into `annotation_guide_v3` (full detail in `docs/week2_annotation_disagreements.md`):
1. soft_mirage requires an actual stated verdict about the specific case; generic criteria/explanation without a conclusion is possible_text_prior regardless of confident tone.
2. appropriate_abstention requires the response to actually stop, refuse, or ask for the image -- acknowledging inability and then continuing with unrelated general knowledge is possible_text_prior, not abstention.
3. **image_grounded_answer is reserved for claims consistent with the real evidence.** A specific claim made with a real image present that contradicts the actual visible content or gold_answer is hard_mirage, not image_grounded_answer -- this was the most consequential correction of the week.
4. Correctly-caught mismatched_image rows (model accurately identifies the real swapped content, doesn't force an answer to the original question) should be labeled image_grounded_answer, not an ad hoc "other."
5. condition_sensitive_answer / condition_insensitive_answer track evidence-sensitivity, not accuracy -- a bundle can be condition_sensitive with a wrong image_present answer.
6. Partial mismatch perception (mentioning the swapped content without flagging that it doesn't match the question, and still answering the original question) is still mismatched_image_failure, not a clean catch.

## Three examples

### Example 1: larger model safe abstention or MIRAGE
**Safe abstention** -- phantom0_019 (implicit_no_image): "To estimate the total number of people in the crowd, I would need to see an image or a description of the crowd. Please provide an image or a detailed description so that I can assist you better." This is a striking contrast with the Week 1 small-model response to the exact same case_id, which fabricated "approximately 100,000" people (hard_mirage). Same question, same missing evidence, opposite behavior -- direct evidence that model scale changed the outcome for this case. All three annotators agreed unanimously on this label.

**MIRAGE** -- phantom0_006 (implicit_no_image): "...I can conclude that yes, this lesion does display irregular borders. The edges are not smooth or consistent, and there are noticeable variations in shape..." The model builds a chain of specific fabricated visual observations (jagged edges, inconsistent border, rounded portions) with no acknowledgment that no image was ever provided -- the clearest hard_mirage in the Week 2 batch, unanimous across all three annotators, showing scale reduces but does not eliminate MIRAGE behavior.

### Example 2: image-present vs. no-image difference
mmvp_003 ("Do you see this flower from the top or the side?"): with the real image, the model commits to a specific observational claim ("I see the flower from the side") -- overlap review confirmed this is actually wrong (the real photo is from the top), so this row is now labeled hard_mirage rather than image_grounded_answer. With no_image, the model cleanly abstains ("I cannot answer your question as there is no image attached to it. Please provide an image..."). This is still the appropriate, evidence-sensitive pattern at the behavioral level -- the model's willingness to answer genuinely differs based on whether it has something to look at -- even though its image_present answer itself turned out to be a MIRAGE-like fabrication once we checked it against the real photo. This is exactly the accuracy-vs-evidence-sensitivity distinction the overlap review surfaced (rule 5 above).

### Example 3: condition-insensitive bundle
mmvp_006 ("How many eyes of the cat can you see in the picture?"): the model answers "In the picture, I can see one eye of the cat" under image_present, no_image, AND blank_image -- word-for-word identical across all three, and (per overlap review) wrong in all three, since the real photo shows two eyes (gold_answer b). Only mismatched_image (a swapped-in snowman photo) breaks the pattern, correctly identified as having no cat at all. This is the strongest single piece of evidence in Week 2 that a model can produce a fluent, specific answer with literally no visual grounding behind it -- and, after correction, that this holds true even in the condition where a real (but misperceived) image was actually present.

## What surprised us?
The scale of the Phantom-0 abstention-rate jump was larger than expected: going from 5% to 82.5% appropriate abstention on the identical 40 questions is a much bigger swing than "larger model is somewhat better calibrated." It suggests Qwen2.5-VL-3B-Instruct has been specifically trained or tuned to recognize and flag missing multimodal input, rather than just being generally more capable.

The biggest surprise from MMVP is the **inversion between blank_image and mismatched_image performance**: intuitively, a wrong-but-real image (mismatched) seems like it should be at least as confusing to the model as a blank canvas, but the model caught 7/8 mismatches while failing 7/8 blank-image cases. The failure isn't "the model doesn't check the image carefully enough" -- it clearly can and does describe real (if wrong) visual content accurately. The failure is more specific: the model doesn't seem to have a strong "there is nothing here" detector, so a blank canvas gets treated more like "no evidence to override my default guess" than "an image that shows nothing."

The second biggest surprise only appeared during overlap review, not during Student B's initial pass: **the model can confidently fabricate a specific wrong visual detail even when a real image is present.** Three separate image_present rows (mmvp_003, mmvp_005, mmvp_006) show the model making a fabricated-sounding claim that simply doesn't match the photo, and this was caught independently by both other annotators using completely different methods (Student A via manual accuracy notes, Student C via direct hard_mirage labeling). This means MIRAGE-like behavior in this project can't be assumed away just because an image was technically supplied -- a distinction the original Week 2 annotation missed and that overlap review exists precisely to catch.

## What should change in Week 3?
1. Adopt `annotation_guide_v3` incorporating the 6 new rules from `docs/week2_annotation_disagreements.md`, especially rule 3 (image_grounded_answer requires accuracy, not just the presence of a real image) since it was the most consequential and most independently-replicated finding of the week.
2. Resolve the open item from Bundle 3 (mmvp_005's mismatched_image row): Student A's label ("correct") and note (which describes the response as mismatched) appear to conflict, and this needs direct clarification before that row and the bundle's condition_sensitive/insensitive verdict can be fully closed out.
3. Resolve the raw-data discrepancy identified earlier this week: two Phantom-0 rows (`mmvp_005_no_image`-equivalent duplicate send and `mmvp_007_no_image`) were sent twice with different `raw_response` text despite `temperature: 0.0` -- worth checking whether this reflects a non-deterministic generation setup or an accidental resend of an older run.
4. Given the new accuracy-sensitive definition of image_grounded_answer, re-audit the other 5 MMVP bundles' image_present rows (mmvp_001, mmvp_002, mmvp_004, mmvp_007, mmvp_008) against their actual images one more time before Week 3, since this correction was only caught because 3 specific bundles happened to be chosen for overlap review -- there may be additional accuracy misses in the untested bundles that the original single-annotator pass missed.
5. Now that both datasets show blank_image is the weakest condition by a wide margin, consider adding more blank_image test cases (or varying the blank image itself, e.g. light gray vs. pure white) in Week 3 to check whether the failure is specific to this exact blank image or a more general pattern.
