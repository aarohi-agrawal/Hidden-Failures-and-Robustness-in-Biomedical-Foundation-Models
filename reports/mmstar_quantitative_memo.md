# MMStar - Quantitative Memo

## Research Question

Does evidence-awareness behavior reproduce outside MMVP?

## Experiment Setup

- 60 frozen MMStar cases (10 cases per capability)
- 5 different evidence conditions (correct_image, no_image, blank_image, far/hard_mismatch)
- 3 models (SmolVLM, Qwen 3B, Qwen 7B)
- 900 outputs (300 per model)
- 120-output human audit
- deterministic and GPT-based answer parsing

## Annotation Results + Agreement

120 of the 900 total outputs were annotated in the human audit.  These outputs were sampled by source id using a saved random seed of 42.

The results are as follows:

- 96.64% agreement for decision
- 87.39% agreement for response_mode
- 73.65% agreement for evidence_issue_stated
- 90.00% agreement for specific_visual_claim

- Cohen's κ of 0.96 for decision (0.9664 - 0.1696) / (1 - 0.1696)
- Cohen's κ of roughly 0.76 for response_mode (0.8739 - 0.4705) / (1 - 0.4705)
- Cohen's κ of 0.30 for evidence_issue_stated (0.7365 - 0.6214) / (1 - 0.6214)
- Cohen's κ of 0.80 for specific_visual_claim (0.9 - 0.5089) / (1 - 0.5089)

Given the generally high percent agreement and Cohen’s kappa for each of the fields, it should be safe to continue running the GPT-5 parser on the rest of the outputs.

## Evidence Performance

T3-A:
| Correct-Img Accuracy | No-Img Gold Match | Blank Gold Match | Far Gold Match | Hard Gold Match | Hard Gap |
| --- | --- | --- | --- | --- | --- |
| SmolVLM | 28.33% | 18.33% | 31.67% | 25.00% | 16.76% | 11.67% |
| Qwen 3B | 46.67% | 15.00% | 38.33% | 16.67% | 16.67% | 30.00% |
| Qwen 7B | 36.67% | 6.67% | 15.00% | 6.67% | 16.67% | 19.20% |

These results suggest that SmolVLM had the highest rates of mirage reasoning and evidence misinterpretation. Their gold match percentages under invalid evidence conditions show that there was likely little explicit abstention, and that the model relied heavily on guessing answers instead. This is also proven by the low hard-mismatch evidence dependence gap of 11.67%, implying a low dependency on valid visual evidence.

Additionally, the results show an overall much lower rate of invalid evidence gold matches among the Qwen models, and much higher correct-image accuracy and evidence dependence (41.67% & 24.60% average vs. 28.33% & 11.67%). From these results, the Qwen models seem to rely much more on valid visual evidence.

## Evidence Awareness

T3-B:
| No-Img Appropriate Response | Blank Blindness | Far Blindness | Hard Blindness | Hard Invariance |
| --- | --- | --- | --- | --- | --- |
| SmolVLM | 0.00% | 100.00% | 93.33% | 93.33% | 51.67% |
| Qwen 3B | 36.67% | 15.00% | 38.33% | 16.67% | 16.67% |
| Qwen 7B | 51.67% | 45.00% | 15.00% | 45.00% | 26.67% |

These results suggest a consistent increase in appropriate response rates across models, going from 0.00%, to 36.67%, to 51.67% as the model size increases.  

However, this consistent improvement in performance does not occur across all fields.  For example, despite Qwen 7B being a larger model, it has significantly higher blindness rates (45.00% each) for blank and hard mismatched images than Qwen 3B (15.00% and 16.67%, respectively).

Although Qwen 7B's behavior is a bit unexpected, it performed similarly to Qwen 3B when compared to SmolVLM.  SmolVLM had a 100% blank image blindness rate, while both of the Qwen models had a rate under 50%. Additionally, the Qwen models had much lower rates of hard invariance.

The main information that can be concluded from these results is that the larger models were more likely to behave differently across different evidence conditions, and much more likely to address invalid or missing evidence and appropriately abstain from answering.