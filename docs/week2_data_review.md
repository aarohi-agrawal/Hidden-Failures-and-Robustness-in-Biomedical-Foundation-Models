# Data Review Notes

## MMVP Data Path
The shared MMVP data folder is located at the following path: 

## Questions.csv Inspection
### 1. How many rows are there?
There are 300 rows of questions in Questions.csv.

### 2. What columns are present?
Not including the question index column, there are three columns: **Question**, **Options**, and **Correct Answer**.  The Question column lists the question, the Options column lists the different response options a model can give, and the Correct Answer column lists the correct answer.

### 3. What is the question field called?
The question field is called **Question**.

### 4. What is the answer field called?
The answer field is called **Correct Answer**.

### 5. How does each row map to an image?
Each row contains a question about the image with a matching index.  For example, the question at index 1 references the image 1.jpg.  These questions are all duplicates and map to pairs of similar images with different correct answers.

### 6. Are images numbered consistently?
Images are all numbered consistently from 1-300.

### 7. Are categories or visual patterns available?
There don't appear to be set categories for image.  Each question and image comes in a pair, with the questions being identical and the images depicting similar scenes with a key visual difference.

## Blank Image Generation
### 1. What is the size of the image?
The blank white image has a size of 224 x 224.

### 2. How was the image created?
The image was created through Python in the terminal using the following commands:

```img = Image.new("RGB", (224, 224), "white")```
```img.save("data/generated/blank_image_white.png")```

### 3. What is the file path?
`data/generated/blank_image_white.png`
