# MMStar - Input Validation

## Seed Set Requirements:

### 60 Unique Source ID Values
Each of the 60 rows contains a unique source ID between 0-1499.

### 10 Cases per Core Category
Every set of 10 rows belongs to one of the core categories: coarse perception, fine-grained perception, instance reasoning, logical reasoning, math, or science & technology.

## Bundle Requirements:

### Valid Image Paths for Correct/Blank/Far/Hard Rows
All rows containing images are matched to the appropriate image path.

- correct_image rows contain the original image path
- blank_image rows contain the path to a blank white image
- far_mismatch rows contain the path to an image in a different category
- hard_mismatch rows contain the path to a related image in the same category + the same l2_category, when possible

### Valid Image Paths for No Image Rows
All no_image rows are ran without any provided image path.

### Far/Hard Mismatch ID != Source ID
None of the rows use mismatch IDs that are equivalent to their source ID.

### Human-Reviewed Mismatch Mappings
All mismatched images were manually compared with the original questions & images and checked for appropriateness.

- far_mismatch images are not relevant to the original question
- hard_mismatch images are relevant to the original question + can provide a plausible answer

## Smoke Test Report