"""Main evaluation script for task-tool matchers."""

import json
import os
from datetime import datetime

from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatcherType

from .data_loader import find_evaluation_data_file, load_evaluation_data
from .evaluator import evaluate_matcher
from .metrics import print_evaluation_summary


def save_results(results: dict, base_output_dir: str) -> str:
    """Save evaluation results to JSON file in results directory.

    Creates: evaluation_results/{matcher_type}_{timestamp}.json

    Args:
        results: Evaluation results dictionary
        base_output_dir: Base directory for results (defaults to evaluate directory)

    Returns:
        Path to saved file
    """
    if base_output_dir is None:
        base_output_dir = os.path.dirname(__file__)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    matcher_type = results.get("matcher_type", "unknown")

    # Create results directory
    results_dir = os.path.join(base_output_dir, "evaluation_results")
    os.makedirs(results_dir, exist_ok=True)

    # Save results file directly in evaluation_results directory
    output_file = os.path.join(results_dir, f"{matcher_type}_{timestamp}.json")

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    return output_file


def main():
    """Main evaluation function."""
    try:
        # Find and load evaluation data
        data_file = find_evaluation_data_file()
        data = load_evaluation_data(data_file)
        print(f"Loaded {len(data)} evaluation entries")

        # Evaluate the RANDOM matcher
        results = evaluate_matcher(TaskToolMatcherType.RANDOM, data)

        # Print summary
        print_evaluation_summary(results)

        # Save detailed results to evaluate directory
        output_file = save_results(results)
        print(f"\nDetailed results saved to: {output_file}")

    except Exception as e:
        print(f"Error during evaluation: {e}")
        raise


if __name__ == "__main__":
    main()
