# Custom Task Example: Movie Review Sentiment Analysis

This directory contains a complete example of a custom task for the NLP Benchmark Platform.

## Contents

- `task.yaml` - Task definition file
- `test_data.jsonl` - Test dataset (10 samples)
- `validation_data.jsonl` - Validation dataset (5 samples)
- `README.md` - This documentation

## Task Description

This task performs binary sentiment classification on movie reviews. Models are asked to classify each review as either "positive" or "negative".

## Dataset Format

Each line in the JSONL files contains a JSON object with:
- `review_text`: The movie review text
- `sentiment`: The ground truth label (0 for negative, 1 for positive)

Example:
```json
{"review_text": "This movie was absolutely fantastic!", "sentiment": 1}
```

## How to Use

### Option 1: Upload via UI

1. Create a ZIP file containing all files in this directory:
   ```bash
   zip -r movie_review_sentiment.zip task.yaml test_data.jsonl validation_data.jsonl README.md
   ```

2. Open the platform UI at http://localhost:3000

3. Navigate to "Upload Task"

4. Drop the ZIP file or click to browse

5. The task will be validated and registered

6. Test with 5 samples using the "Test Task" button

7. Use in benchmark runs via "New Run"

### Option 2: Upload via API

```bash
curl -X POST http://localhost:8000/api/tasks/upload \
  -F "file=@movie_review_sentiment.zip"
```

## Customization

You can modify this example to create your own tasks:

1. **Change the task type**: Update `task_type` in `task.yaml` to one of:
   - `classification`, `multilabel`, `ner`, `summarization`, `qa`, `similarity`, `nli`, `translation`, `freeform`

2. **Update input fields**: Modify `input_fields` to match your dataset schema

3. **Adjust the prompt**: Edit `prompt_template` to customize how the model is prompted

4. **Add more metrics**: Include additional metrics from the supported list for your task type

5. **Expand the dataset**: Add more samples to the JSONL files for better evaluation

## Supported Metrics by Task Type

- **classification**: accuracy, f1_macro, f1_micro, f1_weighted, precision, recall
- **ner**: ner_f1, ner_precision, ner_recall
- **summarization**: rouge1, rouge2, rougeL
- **qa**: exact_match, f1_qa
- **similarity**: pearson, spearman
- **translation**: bleu, chrf

## Best Practices

1. **Balanced datasets**: Ensure your dataset has a good balance of different classes/labels

2. **Clear prompts**: Make the prompt template clear and specific about what you want the model to output

3. **Validation data**: Include a validation split for development and testing

4. **Documentation**: Add a README to explain your task and dataset

5. **Test first**: Use the "Test Task" feature with a small sample before running full benchmarks

## Example Results

After running this task, you'll see metrics like:

- **Accuracy**: Overall correctness of predictions
- **F1 Macro**: Balanced F1 score across both classes
- **Precision**: Proportion of positive predictions that are correct
- **Recall**: Proportion of actual positives that are identified

You'll also see:
- Latency statistics (avg, p50, p95, p99)
- Token usage and cost estimates
- Raw model outputs for inspection
