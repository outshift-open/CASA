"""Metrics calculation and formatting utilities."""

from typing import Any, Dict, List

from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score


def calculate_metrics(y_true: List[bool], y_pred: List[bool]) -> Dict[str, Any]:
    """Calculate evaluation metrics from predictions.

    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels

    Returns:
        Dictionary containing calculated metrics
    """
    if not y_true or not y_pred:
        return {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "confusion_matrix": {"true_positives": 0, "true_negatives": 0, "false_positives": 0, "false_negatives": 0},
        }

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "confusion_matrix": {
            "true_positives": int(tp),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
        },
    }


def print_evaluation_summary(results: Dict[str, Any]) -> None:
    """Print a formatted summary of evaluation results.

    Args:
        results: Dictionary containing evaluation results
    """
    matcher_type = results.get("matcher_type", "UNKNOWN")

    print(f"\n{'=' * 60}")
    print(f"EVALUATION SUMMARY - {matcher_type.upper()} MATCHER")
    print(f"{'=' * 60}")

    print(f"Total entries: {results.get('total_entries', 0)}")
    print(f"Processed entries: {results.get('processed_entries', 0)}")

    print("\nPerformance Metrics:")
    print(f"  Accuracy:  {results.get('accuracy', 0):.3f}")
    print(f"  Precision: {results.get('precision', 0):.3f}")
    print(f"  Recall:    {results.get('recall', 0):.3f}")
    print(f"  F1 Score:  {results.get('f1_score', 0):.3f}")

    cm = results.get("confusion_matrix", {})
    print("\nConfusion Matrix:")
    print(f"  True Positives:  {cm.get('true_positives', 0)}")
    print(f"  True Negatives:  {cm.get('true_negatives', 0)}")
    print(f"  False Positives: {cm.get('false_positives', 0)}")
    print(f"  False Negatives: {cm.get('false_negatives', 0)}")
