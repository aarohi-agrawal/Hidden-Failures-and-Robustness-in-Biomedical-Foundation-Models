# Data Access and Licenses

## MIRAGE / Phantom-0 source

For Week 0, I used the MIRAGE GitHub repository as the source for Phantom-0.

Source: https://github.com/masadi-99/MIRAGE

The Phantom-0 file I inspected was located at:

`data/phantom_0/phantom_0.json`

## What data is included in the MIRAGE repository?

The MIRAGE repository includes the Phantom-0 JSON file used for this Week 0 seed manifest. Phantom-0 contains visual questions but does not include image files.

For the Week 0 handoff, I created a 20-row seed manifest from Phantom-0:

`data/manifests/phantom0_seed.csv`

## What data must be downloaded separately?

At this stage, I only used the Phantom-0 JSON file included in the MIRAGE repository. I did not download any external image datasets or restricted medical data.

Other MIRAGE experiments or related benchmarks may require separate datasets or additional downloads, but I did not use those for the Week 0 Phantom-0 seed file.

## Does Phantom-0 include images?

No. Phantom-0 does not include images. It is a no-image benchmark: it asks visual questions without providing the corresponding visual evidence.

This is intentional because the benchmark is designed to test whether a VLM acknowledges missing image evidence or answers as if it saw an image.

## Is the license clear?

The license and redistribution status should be confirmed before any public release of the project artifacts.

## Are we allowed to redistribute the data?

I am not assuming redistribution is allowed. The 20-row seed manifest was created for internal Week 0 project setup, and redistribution should be confirmed with the mentor before any public release.

## What should we ask the mentor before public release?

We should ask whether MIRAGE / Phantom-0 data can be redistributed in our repository or final release package.

Until confirmed:

MIRAGE / Phantom-0 redistribution requires mentor confirmation before public release.

## Notes

No credentials, private images, restricted medical images, or large source datasets were added.
