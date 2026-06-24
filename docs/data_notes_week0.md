# Week 0 Data Notes

## Phantom-0 location

I inspected the MIRAGE repository and found Phantom-0 under:

`data/phantom_0/`

## Files found

The main file used for Week 0 is:

`phantom_0.json`

## Number of examples

There are 200 examples in `phantom_0.json`.

## Fields observed

Each example has the following fields:

- `id`
- `category`
- `domain`
- `question`
- `risk_level`
- `question_type`

## Does Phantom-0 include images?

No. Phantom-0 does not include images. It contains visual questions without attached images.

## Notes

One thing that stood out is that Phantom-0 intentionally asks image-based questions without providing images. This makes it useful for testing whether a VLM acknowledges missing visual evidence or instead answers as if it saw an image.

I also noticed that the data includes fields like `risk_level` and `question_type`, but our Week 0 CSV only requires `case_id`, `source_id`, `domain`, `category`, `question`, `condition`, `source_repo_commit`, and `notes`.
