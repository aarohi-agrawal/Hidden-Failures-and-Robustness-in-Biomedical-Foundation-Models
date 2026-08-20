# MMStar - Quantitative Memo

## Research Question
Does evidence-awareness behavior reproduce outside MMVP?

## Experiment Setup

- 60 frozen MMStar cases (10 cases per capability)
- 5 different evidence conditions (correct_image, no_image, blank_image, far/hard_mismatch)
- 3 models (SmolVLM, Qwen-3B, Qwen-7B)
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
| Model | Correct-Img Accuracy | No-Img Gold Match | Blank Gold Match | Far Gold Match | Hard Gold Match | Hard Gap |
| --- | --- | --- | --- | --- | --- |
| SmolVLM | 28.33% | 18.33% | 31.67% | 25.00% | 16.76% | 11.67% |
| Qwen-3B | 46.67% | 15.00% | 38.33% | 16.67% | 16.67% | 30.00% |
| Qwen-7B | 36.67% | 6.67% | 15.00% | 6.67% | 16.67% | 19.20% |

These results suggest that SmolVLM had the highest rates of mirage reasoning and evidence misinterpretation. Their gold match percentages under invalid evidence conditions show that there was likely little explicit abstention, and that the model relied heavily on guessing answers instead. This is also proven by the low hard-mismatch evidence dependence gap of 11.67%, implying a low dependency on valid visual evidence.

Additionally, the results show an overall much lower rate of invalid evidence gold matches among the Qwen models, and much higher correct-image accuracy and evidence dependence (41.67% & 24.60% average vs. 28.33% & 11.67%). From these results, the Qwen models seem to rely much more on valid visual evidence.

## Evidence Awareness

T3-B:
| Model | No-Img Appropriate Response | Blank Blindness | Far Blindness | Hard Blindness | Hard Invariance |
| --- | --- | --- | --- | --- | --- |
| SmolVLM | 0.00% | 100.00% | 93.33% | 93.33% | 51.67% |
| Qwen-3B | 36.67% | 15.00% | 38.33% | 16.67% | 16.67% |
| Qwen-7B | 51.67% | 45.00% | 15.00% | 45.00% | 26.67% |

These results suggest a consistent increase in appropriate response rates across models, going from 0.00%, to 36.67%, to 51.67% as the model size increases.  

However, this consistent improvement in performance does not occur across all fields.  For example, despite Qwen-7B being a larger model, it has significantly higher blindness rates (45.00% each) for blank and hard mismatched images than Qwen-3B (15.00% and 16.67%, respectively).

Although Qwen-7B's behavior is a bit unexpected, it performed similarly to Qwen-3B when compared to SmolVLM.  SmolVLM had a 100% blank image blindness rate, while both of the Qwen models had a rate under 50%. Additionally, the Qwen models had much lower rates of hard invariance.

The main information that can be concluded from these results is that the larger models were more likely to behave differently across different evidence conditions, and much more likely to address invalid or missing evidence and appropriately abstain from answering.

## Capability Breakdown

T3-C:
| Model | Capability | n | Correct-Image Accuracy | Blank Blindness | Hard Blindness |
| --- | --- | --- | --- | --- | --- |
| SmolVLM | coarse perception | 10 | 60% | 60% | 30% |
| SmolVLM | fine-grained perception | 10 | 30% | 40% | 20% |
| SmolVLM | instance reasoning | 10 | 10% | 50% | 70% |
| SmolVLM | logical reasoning | 10 | 40% | 60% | 80% |
| SmolVLM | math | 10 | 20% | 50% | 70% |
| SmolVLM | science & technology | 10 | 10% | 40% | 40% |
| Qwen-3B | coarse perception | 10 | 70% | 10% | 20% |
| Qwen-3B | fine-grained perception | 10 | 40% | 20% | 40% |
| Qwen-3B | instance reasoning | 10 | 40% | 0% | 20% |
| Qwen-3B | logical reasoning | 10 | 20% | 30% | 40% |
| Qwen-3B | math | 10 | 30% | 40% | 30% |
| Qwen-3B | science & technology | 10 | 50% | 30% | 30% |
| Qwen-7B | coarse perception | 10 | 40% | 10% | 30% |
| Qwen-7B | fine-grained perception | 10 | 40% | 20% | 30% |
| Qwen-7B | instance reasoning | 10 | 20% | 20% | 10% |
| Qwen-7B | logical reasoning | 10 | 20% | 30% | 20% |
| Qwen-7B | math | 10 | 40% | 20% | 50% |
| Qwen-7B | science & technology | 10 | 30% | 30% | 20% |

Observations:
- Coarse perception had the highest rates of correct image accuracy across models (60%, 70%, and 40%).
- Instance reasoning had the lowest rates of correct image accuracy across models (10%, 40%, and 20%).
- Qwen-7B had the lowest rates of hard mismatch blindness overall (avg. of 26%, compared to 30% for Qwen-3B and 52% for SmolVLM).

These findings show that high correct-image accuracy does not guarantee lower blindness rates for invalid evidence conditions, and that more straightforward capabilities tend to produce more accurate answers.

## Cross-Dataset Comparison

SmolVLM:
- MMVP correct-image accuracy: 55% | MMSTAR correct-image accuracy: 28.33%
- MMVP no-image appropriate response: 10% | MMSTAR no-image appropriate response: 0%
- MMVP blank blindness: 40% | MMSTAR blank blindness: 100%
- MMVP far-mismatch blindness: 47.5% | MMSTAR far-mismatch blindness: 93.33%
- MMVP no-image invariance: 54.3% | MMSTAR no-image invariance: 51.67%
- MMVP blank-image invariance: 50% | MMSTAR blank-image invariance: 36.67%
- MMVP far-mismatch invariance: 50% | MMSTAR far-mismatch invariance: 33.29%

Qwen-3B:
- MMVP correct-image accuracy: 50% | MMSTAR correct-image accuracy: 46.67%
- MMVP no-image appropriate response: 87.5% | MMSTAR no-image appropriate response: 31.67%
- MMVP blank blindness: 40% | MMSTAR blank blindness: 15%
- MMVP far-mismatch blindness: 52.5% | MMSTAR far-mismatch blindness: 38.33%
- MMVP no-image invariance: 40.9% | MMSTAR no-image invariance: 25%
- MMVP blank-image invariance: 32% | MMSTAR blank-image invariance: 21.67%
- MMVP far-mismatch invariance: 44.1% | MMSTAR far-mismatch invariance: 20%

Qwen-7B:
- MMVP correct-image accuracy: 62.5% | MMSTAR correct-image accuracy: 36.67%
- MMVP no-image appropriate response: 67.5% | MMSTAR no-image appropriate response: 51.67%
- MMVP blank blindness: 50% | MMSTAR blank blindness: 45%
- MMVP far-mismatch blindness: 42.5% | MMSTAR far-mismatch blindness: 15%
- MMVP no-image invariance: 75.8% | MMSTAR no-image invariance: 16.67%
- MMVP blank-image invariance: 73.5% | MMSTAR blank-image invariance: 21.67%
- MMVP far-mismatch invariance: 75% | MMSTAR far-mismatch invariance: 10%

## Limitations
- Only 60 MMStar cases were tested, so these results may not accurately represent the full 1,500-case MMStar benchmark.
- An incorrect answer being provided when the correct image is shown does not automatically mean the model failed to understand the image. The error could also come from a misinterpretation of the question or some aspect of the image.
- There were only 10 cases per capability, so the capability-level results aren't necessarily accurate or meaningful.

## Main Takeaway

The main takeaway of the Week 5 MMSTAR results is that evidence-awareness behavior does reproduce outside of MMVP, but it reproduces a bit differently.  MMSTAR showed significantly higher overall blindess than MMVP, and significantly lower answer invariance.

For far-mismatch blindness, SmolVLM was 47.5% on MMVP vs 93.3% on MMStar; Qwen-3B was 52.5% vs 38.3%; Qwen-7B was 42.5% vs 15.0%.
For blank-image blindness, SmolVLM was 40% on MMVP vs 100% on MMStar; Qwen-3B was 40% vs 15%; Qwen-7B was 50% vs 45%.
For blank-image invariance, SmolVLM was 50% on MMVP vs 36.67% on MMStar; Qwen-3B was 32% vs 21.67%; Qwen-7B was 73.5% vs 21.67%.
For far-mismatch invariance, SmolVLM was 50% on MMVP vs 33.29% on MMStar; Qwen-3B was 44.1% vs 20%; Qwen-7B was 75% vs 10%.

Despite Qwen producing lower blindness rates, the overall blindness for MMSTAR is compared to MMVP is higher (Ex. 43.3% vs 53.3% for blank images).

MMStar also showed lower correct-image accuracy for all three models: SmolVLM decreased from 55% on MMVP to 28.33% on MMStar, Qwen-3B from 50% to 46.67%, and Qwen-7B from 62.5% to 36.67%. These results suggest that the MMStar cases were generally more difficult for the models, and produced different patterns of evidence awareness.

Overall, both benchmarks show the same general pattern of models struggling with missing, blank, and mismatched visual evidence, as well as higher gold-answer match rates when visual evidence is provided. This supports the claim that evidence-awareness behavior reproduces across the two benchmarks.


