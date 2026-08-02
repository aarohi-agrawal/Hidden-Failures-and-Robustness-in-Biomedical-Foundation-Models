# Week 3 Input Validation

## Purpose

This document validates that the Week 3 MMVP runner provides the intended visual evidence under each experimental condition.

The four conditions are:

- `image_present`: the correct source image is provided.
- `no_image`: no image is provided.
- `blank_image`: a blank image is provided.
- `mismatched_image`: an image from a different source is provided.

Input validation was performed on three bundles:

- `mmvp_w3_001`
- `mmvp_w3_002`
- `mmvp_w3_003`

The validation included:

1. Manifest-level file and path checks.
2. Runner-level input construction inspection.
3. Runtime processor input inspection.
4. Image dimensions and pixel statistics.
5. Verification of image tensor creation.
6. Verification that no image tensor is created for `no_image`.

---

## 1. Runner-Level Input Handling

The Week 3 runner uses the same standardized prompt for all four conditions. The prompt itself does not describe whether an image is present, blank, or mismatched.

For the three image conditions (`image_present`, `blank_image`, and `mismatched_image`), the runner creates an image message using the `image_path` supplied by the manifest.

For `no_image`, the runner creates a text-only message. No image object is added to the model input.

The runner validates that:

- `no_image` rows have an empty `image_path`.
- Image conditions have a valid existing `image_path`.
- `mismatched_image` rows contain a `mismatch_source_id`.

For image conditions, the runner passes the message through `qwen_vl_utils.process_vision_info()` and then calls the processor with `images=image_inputs`.

For `no_image`, the runner calls the processor with text only and does not pass an `images` argument.

---

## 2. Runtime Processor Validation

Runtime validation was performed using the same processor configuration as the Week 3 small-model run:

`Qwen/Qwen2.5-VL-3B-Instruct`

The 12 validation cases consisted of:

- 3 bundles
- 4 conditions per bundle
- 12 total cases

For all image conditions, the processor produced the following input keys:

- `input_ids`
- `attention_mask`
- `mm_token_type_ids`
- `pixel_values`
- `image_grid_thw`

For all image conditions, an image tensor was created.

The resulting `pixel_values` tensor shape was:

`(256, 1176)`

For all `no_image` cases, the processor produced:

- `input_ids`
- `attention_mask`
- `mm_token_type_ids`

No `pixel_values` tensor was created.

This confirms that the `no_image` condition is implemented as a true text-only input rather than as a blank-image or placeholder-image input.

---

## 3. Bundle `mmvp_w3_001`

### Question

Are the butterfly's wings closer to being open or closed?

### Image-present condition

Image path:

`data/mmvp/MMVP Images/1.jpg`

Image properties:

- Dimensions: 224 × 224
- Mode: RGB
- Minimum pixel value: 0
- Maximum pixel value: 255
- Mean pixel value: 120.5404
- Standard deviation: 63.1825

Runtime processor validation:

- Processor mode: IMAGE
- Vision input type: list
- Number of image inputs: 1
- Image input type: PIL Image
- Image tensor created: Yes
- `pixel_values` shape: `(256, 1176)`

Validation:

The correct source image for `source_id=1` was loaded and converted into an image tensor.

Result: PASS

### No-image condition

Image path:

None

Runtime processor validation:

- Processor mode: TEXT-ONLY
- Processor input keys: `input_ids`, `attention_mask`, `mm_token_type_ids`
- Image tensor created: No
- `pixel_values` present: No

Validation:

The manifest specifies no image path. The runner constructs a text-only message and passes no image object or image tensor to the processor.

Result: PASS

### Blank-image condition

Image path:

`data/generated/week3_blank_images/mmvp_w3_001_blank.png`

Image properties:

- Dimensions: 224 × 224
- Mode: RGB
- Minimum pixel value: 255
- Maximum pixel value: 255
- Mean pixel value: 255.0
- Standard deviation: 0.0

Runtime processor validation:

- Processor mode: IMAGE
- Vision input type: list
- Number of image inputs: 1
- Image input type: PIL Image
- Image tensor created: Yes
- `pixel_values` shape: `(256, 1176)`

Validation:

The loaded image is completely white. The image remains blank after loading, and the processor creates an image tensor from the blank image.

Result: PASS

### Mismatched-image condition

Image path:

`data/mmvp/MMVP Images/162.jpg`

Correct source image:

`data/mmvp/MMVP Images/1.jpg`

Mismatch source ID:

`162`

Image properties:

- Dimensions: 224 × 224
- Mode: RGB
- Minimum pixel value: 0
- Maximum pixel value: 255
- Mean pixel value: 136.0239
- Standard deviation: 79.5579

Runtime processor validation:

- Processor mode: IMAGE
- Vision input type: list
- Number of image inputs: 1
- Image input type: PIL Image
- Image tensor created: Yes
- `pixel_values` shape: `(256, 1176)`

Validation:

The manifest specifies source ID 162 as the mismatched image rather than the correct source image 1. The runtime processor loaded the specified mismatched image and created an image tensor.

Result: PASS

---

## 4. Bundle `mmvp_w3_002`

### Question

Is the duck's entire beak visible in the picture?

### Image-present condition

Image path:

`data/mmvp/MMVP Images/21.jpg`

Image properties:

- Dimensions: 224 × 224
- Mode: RGB
- Minimum pixel value: 0
- Maximum pixel value: 255
- Mean pixel value: 102.6177
- Standard deviation: 53.0915

Runtime processor validation:

- Processor mode: IMAGE
- Vision input type: list
- Number of image inputs: 1
- Image input type: PIL Image
- Image tensor created: Yes
- `pixel_values` shape: `(256, 1176)`

Validation:

The correct source image for `source_id=21` was loaded and converted into an image tensor.

Result: PASS

### No-image condition

Image path:

None

Runtime processor validation:

- Processor mode: TEXT-ONLY
- Processor input keys: `input_ids`, `attention_mask`, `mm_token_type_ids`
- Image tensor created: No
- `pixel_values` present: No

Validation:

The manifest specifies no image path. The runner constructs a text-only message and passes no image object or image tensor to the processor.

Result: PASS

### Blank-image condition

Image path:

`data/generated/week3_blank_images/mmvp_w3_002_blank.png`

Image properties:

- Dimensions: 224 × 224
- Mode: RGB
- Minimum pixel value: 255
- Maximum pixel value: 255
- Mean pixel value: 255.0
- Standard deviation: 0.0

Runtime processor validation:

- Processor mode: IMAGE
- Vision input type: list
- Number of image inputs: 1
- Image input type: PIL Image
- Image tensor created: Yes
- `pixel_values` shape: `(256, 1176)`

Validation:

The loaded image is completely white. The image remains blank after loading, and the processor creates an image tensor from the blank image.

Result: PASS

### Mismatched-image condition

Image path:

`data/mmvp/MMVP Images/183.jpg`

Correct source image:

`data/mmvp/MMVP Images/21.jpg`

Mismatch source ID:

`183`

Image properties:

- Dimensions: 224 × 224
- Mode: RGB
- Minimum pixel value: 0
- Maximum pixel value: 255
- Mean pixel value: 208.2842
- Standard deviation: 68.8892

Runtime processor validation:

- Processor mode: IMAGE
- Vision input type: list
- Number of image inputs: 1
- Image input type: PIL Image
- Image tensor created: Yes
- `pixel_values` shape: `(256, 1176)`

Validation:

The manifest specifies source ID 183 as the mismatched image rather than the correct source image 21. The runtime processor loaded the specified mismatched image and created an image tensor.

Result: PASS

---

## 5. Bundle `mmvp_w3_003`

### Question

Based on the image, is the following statement correct: The spider has 8 legs?

### Image-present condition

Image path:

`data/mmvp/MMVP Images/41.jpg`

Image properties:

- Dimensions: 224 × 224
- Mode: RGB
- Minimum pixel value: 0
- Maximum pixel value: 255
- Mean pixel value: 53.5301
- Standard deviation: 48.6642

Runtime processor validation:

- Processor mode: IMAGE
- Vision input type: list
- Number of image inputs: 1
- Image input type: PIL Image
- Image tensor created: Yes
- `pixel_values` shape: `(256, 1176)`

Validation:

The correct source image for `source_id=41` was loaded and converted into an image tensor.

Result: PASS

### No-image condition

Image path:

None

Runtime processor validation:

- Processor mode: TEXT-ONLY
- Processor input keys: `input_ids`, `attention_mask`, `mm_token_type_ids`
- Image tensor created: No
- `pixel_values` present: No

Validation:

The manifest specifies no image path. The runner constructs a text-only message and passes no image object or image tensor to the processor.

Result: PASS

### Blank-image condition

Image path:

`data/generated/week3_blank_images/mmvp_w3_003_blank.png`

Image properties:

- Dimensions: 224 × 224
- Mode: RGB
- Minimum pixel value: 255
- Maximum pixel value: 255
- Mean pixel value: 255.0
- Standard deviation: 0.0

Runtime processor validation:

- Processor mode: IMAGE
- Vision input type: list
- Number of image inputs: 1
- Image input type: PIL Image
- Image tensor created: Yes
- `pixel_values` shape: `(256, 1176)`

Validation:

The loaded image is completely white. The image remains blank after loading, and the processor creates an image tensor from the blank image.

Result: PASS

### Mismatched-image condition

Image path:

`data/mmvp/MMVP Images/202.jpg`

Correct source image:

`data/mmvp/MMVP Images/41.jpg`

Mismatch source ID:

`202`

Image properties:

- Dimensions: 224 × 224
- Mode: RGB
- Minimum pixel value: 0
- Maximum pixel value: 255
- Mean pixel value: 233.2465
- Standard deviation: 44.1804

Runtime processor validation:

- Processor mode: IMAGE
- Vision input type: list
- Number of image inputs: 1
- Image input type: PIL Image
- Image tensor created: Yes
- `pixel_values` shape: `(256, 1176)`

Validation:

The manifest specifies source ID 202 as the mismatched image rather than the correct source image 41. The runtime processor loaded the specified mismatched image and created an image tensor.

Result: PASS

---

## 6. Summary

All three manually inspected bundles passed runtime input validation.

| Bundle | Correct Image | No Image | Blank Image | Mismatched Image |
|---|---|---|---|---|
| `mmvp_w3_001` | PASS | PASS | PASS | PASS |
| `mmvp_w3_002` | PASS | PASS | PASS | PASS |
| `mmvp_w3_003` | PASS | PASS | PASS | PASS |

The runtime validation confirms:

- Correct images are loaded for `image_present`.
- No image object or image tensor is created for `no_image`.
- Blank images remain uniformly blank after loading.
- Blank images are converted into image tensors as expected.
- Mismatched images are loaded from the manifest-specified mismatch paths.
- Mismatched images are converted into image tensors.
- All image conditions produce `pixel_values` with shape `(256, 1176)`.
- The `no_image` condition produces no `pixel_values`.

This confirms that the Week 3 runner provides distinct and correctly implemented evidence conditions at runtime.

---

## 7. Manual Visual Preview

File-level and runtime validation confirm that the intended files are loaded. Manual visual inspection should also be performed for the three correct source images and three mismatched images:

- `data/mmvp/MMVP Images/1.jpg`
- `data/mmvp/MMVP Images/21.jpg`
- `data/mmvp/MMVP Images/41.jpg`
- `data/mmvp/MMVP Images/162.jpg`
- `data/mmvp/MMVP Images/183.jpg`
- `data/mmvp/MMVP Images/202.jpg`

The three blank images were verified programmatically to be uniformly white with standard deviation 0.0.

Manual visual inspection of the six source/mismatch images is required to confirm semantic identity and should be completed before the final experiment is considered fully validated.

