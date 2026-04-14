# Task-Tool Matcher Evaluation

This directory contains a clean, modular evaluation framework for testing task-tool matchers.

## Overview

The evaluation system tests how well different matchers can determine if a given task should use a specific tool. It loads test data, runs predictions, calculates metrics, and saves results.

## Structure

```
evaluate/
├── __init__.py          # Package initialization
├── data_loader.py       # Data loading utilities
├── evaluator.py         # Core evaluation logic
├── main.py             # Main entry point
├── metrics.py          # Metrics calculation and formatting
└── README.md           # This file
```

## Files Description

### `data_loader.py`
- **Purpose**: Load evaluation data from JSON or compressed files
- **Key Functions**:
  - `load_evaluation_data()`: Load and parse evaluation entries
  - `find_evaluation_data_file()`: Locate data file (prefers compressed)

### `evaluator.py`
- **Purpose**: Core evaluation logic for testing matchers
- **Key Functions**:
  - `evaluate_matcher()`: Run evaluation on a specific matcher type
  - Handles predictions, error handling, and result collection

### `metrics.py`
- **Purpose**: Calculate and display evaluation metrics
- **Key Functions**:
  - `calculate_metrics()`: Compute accuracy, precision, recall, F1, confusion matrix
  - `print_evaluation_summary()`: Format and display results

### `main.py`
- **Purpose**: Main entry point for running evaluations
- **Key Functions**:
  - `main()`: Orchestrate the full evaluation process
  - `save_results()`: Save detailed results with timestamp

## Usage

### Run Evaluation
```bash
# From the project root
python -m evaluation.task_tool_matcher.evaluate.main
```

### Output
The evaluation will:
1. Load test data from `evaluation/task_tool_matcher/data/`
2. Run the specified matcher (currently RANDOM)
3. Print performance metrics to console
4. Save detailed results to `evaluation_results/{matcher}_{timestamp}.json`

## Results Directory Structure

Results are saved as individual JSON files:
```
evaluation_results/
├── random_20250822_152511.json
├── random_20250822_154230.json
└── other_matcher_20250822_160000.json
```

This structure makes it easy to:
- Quickly access individual evaluation results
- Compare results across different runs
- Organize results by matcher type and timestamp

## Metrics

The evaluation calculates standard classification metrics:
- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1 Score**: Harmonic mean of precision and recall
- **Confusion Matrix**: Breakdown of prediction types

## Adding New Matchers

To evaluate a different matcher:
1. Update `TaskToolMatcherType` enum with new type
2. Modify `main.py` to use the new matcher type
3. Run evaluation
