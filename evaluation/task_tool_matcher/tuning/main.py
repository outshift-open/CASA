"""Main tuning script for task-tool matchers."""

import argparse
import json
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from evaluation.task_tool_matcher.evaluate.data_loader import find_evaluation_data_file, load_evaluation_data
from evaluation.task_tool_matcher.evaluate.evaluator import evaluate_matcher
from evaluation.task_tool_matcher.evaluate.metrics import print_evaluation_summary
from identity_auth_server.pipelines.task_tool_matcher.types import TaskToolMatcherType


def save_results(results: dict, base_output_dir: str) -> str:
    """Save evaluation results to JSON file in results directory.

    Creates: tuning_results/{matcher_type}_{timestamp}.json

    Args:
        results: Tuning results dictionary
        base_output_dir: Base directory for results (defaults to evaluate directory)

    Returns:
        Path to saved file
    """
    if base_output_dir is None:
        base_output_dir = os.path.dirname(__file__)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    matcher_type = results.get("matcher_type", "unknown")

    # Create results directory
    results_dir = os.path.join(base_output_dir, "tuning_results")
    os.makedirs(results_dir, exist_ok=True)

    # Save results file directly in tuning_results directory
    output_file = os.path.join(results_dir, f"{matcher_type}_{timestamp}.json")

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    fig = create_precision_recall_curve(results)
    fig_file = os.path.join(results_dir, f"{matcher_type}_{timestamp}.html")
    fig.write_html(fig_file)

    return output_file


def create_precision_recall_curve(results: dict) -> go.Figure:
    """Create a precision-recall curve from tuning results."""
    precision = []
    recall = []
    thresholds = []
    for run in results.get("runs", []):
        precision.append(run["results"]["precision"])
        recall.append(run["results"]["recall"])
        thresholds.append(run["match_threshold"])

    df = pd.DataFrame({"Recall": recall, "Precision": precision, "Threshold": thresholds})
    fig = px.scatter(
        df,
        x="Recall",
        y="Precision",
        hover_data=["Threshold"],
        title="Precision Recall for {} matcher".format(results.get("matcher_type", "unknown")),
    )
    return fig


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Run TaskToolMatcher evaluation.")
    parser.add_argument(
        "--matcher_type",
        type=str,
        required=True,
        help="Specify the TaskToolMatcherType (e.g., 'random', 'embeddings', etc.)",
    )
    args = parser.parse_args()
    matcher_type_str = args.matcher_type
    threshold_span = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    overall_results = {"matcher_type": matcher_type_str, "runs": []}
    try:
        # Find and load evaluation data
        data_file = find_evaluation_data_file()
        data = load_evaluation_data(data_file)
        print(f"Loaded {len(data)} evaluation entries")

        # Convert string to TaskToolMatcherType
        try:
            matcher_type = TaskToolMatcherType[matcher_type_str.upper()]
        except KeyError:
            raise ValueError(f"Unknown matcher type: {matcher_type_str}")

        for match_threshold in threshold_span:
            results = evaluate_matcher(matcher_type, data, match_threshold=match_threshold)
            print_evaluation_summary(results)
            overall_results["runs"].append(
                {
                    "match_threshold": match_threshold,
                    "results": results,
                }
            )

        # Save detailed results to tuning directory
        output_file = save_results(overall_results, None)
        print(f"\nDetailed results saved to: {output_file}")

    except Exception as e:
        print(f"Error during evaluation: {e}")
        raise


if __name__ == "__main__":
    main()
