"""Core evaluation logic for task-tool matchers."""

from typing import Any, Dict, List

from evaluation.task_tool_matcher.types import EvaluateEntryTaskToolMatcher
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import TaskToolMatcherFactory
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatcherType

from .metrics import calculate_metrics


def evaluate_matcher(
    matcher_type: TaskToolMatcherType, data: List[EvaluateEntryTaskToolMatcher], verbose: bool = True
) -> Dict[str, Any]:
    """Evaluate a task-tool matcher on the given data.

    Args:
        matcher_type: Type of matcher to evaluate
        data: List of evaluation entries
        verbose: Whether to print progress updates

    Returns:
        Dictionary containing evaluation results
    """
    # Create the TaskToolMatcher using the factory
    matcher = TaskToolMatcherFactory.create(matcher_type)

    # Store predictions and ground truth
    y_true = []
    y_pred = []
    predictions = []

    if verbose:
        print(f"Evaluating {matcher_type.value} matcher on {len(data)} entries...")

    # Process each entry
    for i, entry in enumerate(data):
        try:
            # Get prediction from matcher
            result = matcher.match(entry.input)

            # Store prediction and ground truth
            y_true.append(entry.match)
            y_pred.append(result.task_tool_match)

            predictions.append(
                {
                    "index": i,
                    "task": entry.input.task,
                    "requested_tool": entry.input.requested_tool,
                    "ground_truth": entry.match,
                    "prediction": result.task_tool_match,
                    "correct": entry.match == result.task_tool_match,
                    "reason": result.reason.value if result.reason else None,
                }
            )

            if verbose and i % 5 == 0:
                print(f"  Processed {i + 1}/{len(data)} entries...")

        except Exception as e:
            if verbose:
                print(f"Error processing entry {i}: {e}")
            continue

    # Calculate metrics
    metrics = calculate_metrics(y_true, y_pred)

    # Combine results
    results = {
        "matcher_type": matcher_type.value,
        "total_entries": len(data),
        "processed_entries": len(predictions),
        **metrics,
        "predictions": predictions,
    }

    return results
