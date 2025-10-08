"""Core evaluation logic for task-tool matchers."""

from typing import Any, Dict, List

from evaluation.task_tool_matcher.types import EvaluateEntryTaskToolMatcher
from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import TaskToolMatcherFactory
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatcherType, TaskToolMatchInput

from .metrics import calculate_metrics


def evaluate_matcher(
    matcher_type: TaskToolMatcherType,
    data: List[EvaluateEntryTaskToolMatcher],
    tuning_mode: bool = False,
    verbose: bool = True,
    **matcher_kwargs,
) -> Dict[str, Any]:
    """Evaluate a task-tool matcher on the given data.

    Args:
        matcher_type: Type of matcher to evaluate
        data: List of evaluation entries
        tuning_mode: Whether to set the matcher in tuning mode
        verbose: Whether to print progress updates
        matcher_kwargs: Additional keyword arguments for the matcher

    Returns:
        Dictionary containing evaluation results
    """
    # Create the TaskToolMatcher using the factory
    matcher = TaskToolMatcherFactory.create(matcher_type, **matcher_kwargs)
    if tuning_mode:
        matcher.set_tuning_mode()

    # Store predictions and ground truth
    y_true = []
    y_pred = []
    predictions = []

    if verbose:
        print(f"Evaluating {matcher_type.value} matcher on {len(data)} entries...")

    # Process each entry
    for i, entry in enumerate(data):
        try:
            for tool_id, requested_tool in enumerate(entry.input.requested_tools):
                # Get prediction from matcher
                if not entry.input.requested_mcp_servers:
                    raise ValueError(f"Entry {i}: requested_mcp_servers is None or empty")
                if tool_id >= len(entry.input.requested_mcp_servers):
                    raise IndexError(
                        f"Entry {i}: tool_id {tool_id} out of range for requested_mcp_servers (length: {len(entry.input.requested_mcp_servers)})"
                    )

                matcher_input = TaskToolMatchInput(
                    task=entry.input.task,
                    requested_tool=requested_tool,
                    mcp_server=entry.input.requested_mcp_servers[tool_id],
                )
                result = matcher.match(matcher_input)

                match_tag = entry.match_tag
                if not entry.groundtruth.tools:
                    raise ValueError(f"Entry {i}: groundtruth.tools is None or empty")
                if tool_id >= len(entry.groundtruth.tools):
                    raise IndexError(
                        f"Entry {i}: tool_id {tool_id} out of range for groundtruth.tools (length: {len(entry.groundtruth.tools)})"
                    )

                gt_tool = entry.groundtruth.tools[tool_id]
                gt_match = True if gt_tool == requested_tool else False

                # Store prediction and ground truth
                y_true.append(gt_match)
                y_pred.append(result.task_tool_match)

                predictions.append(
                    {
                        "index": i,
                        "tool_id": tool_id,
                        "task": entry.input.task,
                        "requested_tool": requested_tool,
                        "ground_truth": gt_match,
                        "prediction": result.task_tool_match,
                        "correct": gt_match == result.task_tool_match,
                        "reason": result.reason.value if result.reason else None,
                        "match_tag": match_tag,
                        "debug": result.debug,
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
