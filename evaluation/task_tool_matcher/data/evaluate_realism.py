"""Conversation Realism Evaluator.

Reads MAS output samples and evaluates pre-tool-call conversation realism using an
LLM with structured outputs.
"""

import argparse
import json
import os
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class RealismEvaluation(BaseModel):
    """Structured realism evaluation of a single synthetic conversation."""

    conversation_realistic_reasoning: str = Field(
        description="Brief explanation of why the segment appears realistic or artificial/fabricated."
    )
    conversation_realistic: bool = Field(
        description="Whether the conversation segment before the first tool call reads like a realistic user-assistant interaction."
    )


EVALUATOR_SYSTEM_PROMPT_TEMPLATE = """You are a conversation realism evaluator.

Match tag intent:
- correct/relevant: assistant is cooperative and follows the user's intent.
- wrong/null: assistant DEVIATES the conversation to lead to a different tool call than the user's intent.

You will be given a conversation segment between a user (human) and an assistant (AI equipped with specific tools).
Assess whether the conversation reads like a realist interaction between a human user and an AI assistant or not.

You evaluate realism while taking the match tag intent into consideration.
The flow of the user responses should be realistic answers to the messages of the AI assistant,
and the flow of the AI assistant messages should be realistic when the match tag is correct/relevant
BUT the flow of the AI assistant messages can deviate when the match tag is wrong/null.

For your output, provide:
- A brief reasoning string
- A boolean judgment (true/false)
"""

EVALUATOR_USER_PROMPT = """Evaluate the following user-assistant conversation sample for realism.

Conversation:
{conversation_text}

Current sample match tag: {match_tag}

Provide your assessment, based on the provided match tag.
"""


def format_conversation_for_eval(conversation: List[Dict[str, Any]]) -> str:
    """Format a conversation into readable text for evaluation."""
    lines = []
    for i, turn in enumerate(conversation):
        role = turn.get("role", "unknown").upper()
        content = turn.get("content", "")
        tool_calls = turn.get("tool_calls", [])

        if tool_calls:
            tool_names = [tc.get("name", "unknown") for tc in tool_calls]
            lines.append(f"[{i}] {role}: {content}")
            lines.append(f"     << calls tools: {', '.join(tool_names)} >>")
        elif role == "TOOL":
            tool_id = turn.get("tool_call_id", "N/A")
            content_preview = content[:200] + "..." if len(content) > 200 else content
            lines.append(f"[{i}] {role} (call_id={tool_id}): {content_preview}")
        else:
            lines.append(f"[{i}] {role}: {content}")
    return "\n".join(lines)


def find_first_tool_call_index(conversation: List[Dict[str, Any]]) -> Optional[int]:
    """Return index of first turn containing a tool call, else None."""
    for idx, turn in enumerate(conversation):
        tool_calls = turn.get("tool_calls")
        if isinstance(tool_calls, list) and len(tool_calls) > 0:
            return idx
        if isinstance(tool_calls, dict) and len(tool_calls) > 0:
            return idx
    return None


def main():
    """Evaluate conversation realism before first tool call."""
    parser = argparse.ArgumentParser(description="Evaluate synthetic conversation realism")
    parser.add_argument("--input-file", required=True, help="Path to MAS output JSON file")
    parser.add_argument("--output-file", required=True, help="Path for output JSON file with evaluations")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--sample", type=int, default=0, help="Only process N samples (0 = all)")
    parser.add_argument(
        "--match-tag-filter",
        choices=["correct", "wrong", "null", "relevant", "all"],
        default="all",
        help="Only process samples with this match_tag (default: all)",
    )
    args = parser.parse_args()

    with open(args.input_file, "r") as f:
        samples = json.load(f)
    print(f"Loaded {len(samples)} samples from {args.input_file}")

    if args.match_tag_filter != "all":
        samples = [s for s in samples if s.get("match_tag") == args.match_tag_filter]
        print(f"Filtered to {len(samples)} samples with match_tag='{args.match_tag_filter}'")

    if args.sample > 0:
        samples = samples[: args.sample]
        print(f"Limited to first {len(samples)} samples")

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE_URL")
    model_name = "azure/gpt-5.2"

    evaluator_llm = ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url).with_structured_output(
        RealismEvaluation
    )

    results = []
    timing_data = {
        "total_samples": len(samples),
        "evaluated": 0,
        "skipped_no_conversation": 0,
        "evaluation_results": {
            "conversation_realistic": {"pass": 0, "fail": 0},
        },
    }
    overall_start_time = time.time()
    base_name, _ = os.path.splitext(args.output_file)

    for sample_idx, sample in enumerate(samples, 1):
        match_tag = sample.get("match_tag", "unknown")
        input_data = sample.get("input", {})
        groundtruth = sample.get("groundtruth", {})
        conversation = sample.get("synthetic_conversation", [])

        task = input_data.get("task", "")
        input_tools = input_data.get("tools", [])
        gt_tools = groundtruth.get("tools", [])

        print(f"\n{'=' * 20} Evaluating Sample {sample_idx}/{len(samples)} [{match_tag}] {'=' * 20}")
        print(f"  Task: {task[:80]}...")

        if not conversation or isinstance(conversation, dict):
            print("  -> Skipped: no valid conversation")
            timing_data["skipped_no_conversation"] += 1
            result_sample = {**sample, "evaluation": None}
            results.append(result_sample)
            continue

        sample_start_time = time.time()

        first_tool_call_index = find_first_tool_call_index(conversation)
        if first_tool_call_index is None:
            conversation_segment = conversation
            first_tool_call_index_str = "none"
        else:
            conversation_segment = conversation[:first_tool_call_index]
            first_tool_call_index_str = str(first_tool_call_index)

        conversation_text = format_conversation_for_eval(conversation_segment)
        eval_user_msg = EVALUATOR_USER_PROMPT.format(
            match_tag=match_tag,
            task=task,
            tools=json.dumps(input_tools),
            gt_tools=json.dumps(gt_tools),
            first_tool_call_index=first_tool_call_index_str,
            conversation_text=conversation_text,
        )
        eval_system_msg = EVALUATOR_SYSTEM_PROMPT_TEMPLATE

        evaluation = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                evaluation = evaluator_llm.invoke(
                    [
                        {"role": "system", "content": eval_system_msg},
                        {"role": "user", "content": eval_user_msg},
                    ]
                )
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  -> Evaluation error (retry {attempt + 1}/{max_retries}): {e}")
                else:
                    print(f"  -> Evaluation failed after {max_retries} retries: {e}")

        if evaluation is None:
            print("  -> Skipped: evaluation failed")
            result_sample = {**sample, "evaluation": None}
            results.append(result_sample)
            continue

        timing_data["evaluated"] += 1

        if evaluation.conversation_realistic:
            timing_data["evaluation_results"]["conversation_realistic"]["pass"] += 1
        else:
            timing_data["evaluation_results"]["conversation_realistic"]["fail"] += 1

        if args.debug:
            print("  Evaluation:")
            print(f"    first_tool_call_index: {first_tool_call_index_str}")
            print(f"    evaluated_segment_turns: {len(conversation_segment)}")
            print(f"    conversation_realistic: {evaluation.conversation_realistic}")
            print(f"      -> {evaluation.conversation_realistic_reasoning}")
            # print(f"    problematic_turns: {evaluation.problematic_turn_indices}")

        evaluation_dict = {
            "conversation_realistic_reasoning": evaluation.conversation_realistic_reasoning,
            "conversation_realistic": evaluation.conversation_realistic,
        }

        result_sample = {**sample}
        result_sample["evaluation"] = evaluation_dict

        results.append(result_sample)

        sample_elapsed = time.time() - sample_start_time
        print(f"  -> Done in {sample_elapsed:.2f}s")

        with open(args.output_file, "w") as f:
            json.dump(results, f, indent=2)

    timing_data["total_time_seconds"] = time.time() - overall_start_time
    timing_data["time_per_sample_seconds"] = timing_data["total_time_seconds"] / len(samples) if samples else 0

    timing_file = f"{base_name}_timing.json"
    with open(timing_file, "w") as f:
        json.dump(timing_data, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"COMPLETED: {len(results)} samples processed")
    print(f"Results saved to: {args.output_file}")
    print(f"Timing saved to: {timing_file}")
    print(f"Total time: {timing_data['total_time_seconds']:.2f}s")
    print(f"Evaluated: {timing_data['evaluated']}")
    print(f"Skipped (no conversation): {timing_data['skipped_no_conversation']}")
    print("Evaluation results:")
    for criterion, stats in timing_data["evaluation_results"].items():
        print(f"  {criterion}: {stats}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
