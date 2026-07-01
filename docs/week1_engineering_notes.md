## Week 1 Engineering Notes

### What model did we run?
We chose to run HuggingFaceTB/SmolVLM-256M-Instruct, the same model used for last week's smoke test.

### Does the model support no-image prompts?
The model seems to support no-image prompts, as no errors came up when reading any of the 40 rows.  However, the model would occasionally obstain from answering a question without a provided image.

### What command did we run?
The command used to run the script is as follows: **python3 src/adapters/run_phantom0_week1.py**.

### How many rows succeeded? How many failed?
All 40 rows succeeded, without any sort of error message or unusual behavior.  None of the rows failed.

### What errors occurred?
No errors occurred with this particular model and set of questions.

### How long did the run take?
With the help of python's time module, I was able to record the amount of time taken for a full run, which was around 14.6 seconds.

### What should be fixed before Week 2?
Everything seemed to run smoothly this week for the most part.  However, for the sake of reusability it would likely be better not to hardcode the file path and model name in the run script.