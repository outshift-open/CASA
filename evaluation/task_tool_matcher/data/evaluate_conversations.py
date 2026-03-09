"""Conversation Quality Evaluator.

Reads MAS output samples and evaluates each conversation for realism and identity
leakage using an LLM with structured outputs.
"""

import argparse
import json
import os
import time
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

# ── Structured Output Models ──────────────────────────────────────────────────

FINDINGS_SUMMARY = """You are a conversation quality evaluator for a synthetic multi-agent simulation dataset.
These conversations are between a simulated human user and an AI assistant that has access to tools.
A tool simulator provides fake but realistic tool outputs (no real APIs are called).

The following quality issues have been identified in prior analysis of this dataset.
Use them as your evaluation rubric. Focus ONLY on the USER role messages when evaluating
realism — ignore whether assistant responses are accurate, helpful, or well-formed.

1. USER IDENTITY LEAKAGE: The user agent sometimes produces phrases that reveal it is
   an LLM rather than a human. Examples: "I am trained on data up to...", "As an AI...",
   "I don't have real-time access...", "I'm an AI language model...", offering unsolicited
   technical explanations, or using overly formal/robotic phrasing no human would use.
   A real human user would never say these things.

2. TOOL SIMULATOR SCHEMA MISMATCH: The tool simulator returns data that does not match
   what the called tool would logically produce given its purpose and schema. For example,
   a weather tool returning database query results, or a file search tool returning
   financial data. The tool output should be consistent with the tool's described
   functionality, regardless of what the user actually needs.

3. STUCK LOOPS: The assistant calls the same tool multiple times (3+) with identical
   or near-identical arguments, getting the same results each time. This creates
   redundant, unrealistic conversation turns.
"""


class ConversationEvaluation(BaseModel):
    """Structured evaluation of a single synthetic conversation."""

    conversation_realistic: bool = Field(
        description="Whether ALL user messages throughout the conversation read as realistic human utterances. Ignore assistant message quality entirely — only evaluate whether user turns sound like a real person. Consider natural phrasing, coherent responses to the assistant, and absence of LLM-like language."
    )
    conversation_realistic_reasoning: str = Field(
        description="Brief explanation of why user messages are or are not realistic. Reference specific user turns only."
    )
    pre_tool_call_realistic: bool = Field(
        description="Whether user messages UP TO AND INCLUDING the first tool call are realistic. If there are no tool calls, evaluate all user messages. Focus only on whether the user's request and follow-up messages sound like a real human — ignore the assistant's tool selection or responses."
    )
    pre_tool_call_realistic_reasoning: str = Field(
        description="Brief explanation of why the user messages in the pre-tool-call portion are or are not realistic. Reference specific user turns only."
    )
    user_identity_leakage: bool = Field(
        description="Whether the USER agent reveals it is an LLM at any point. Look for phrases like 'I am trained on...', 'As an AI...', 'I don't have real-time access...', overly formal/robotic language, unsolicited technical disclaimers, or any other phrasing that a real human would never use when asking for help."
    )
    user_identity_leakage_reasoning: str = Field(
        description="Brief explanation of whether and where user identity leakage occurs. Quote the specific problematic text if found."
    )
    tool_mismatch: bool = Field(
        description="Whether the tool simulator returns data that does not match what the called tool would logically produce given its purpose and schema. For example, a weather tool returning database query results, or a file search tool returning financial data. The tool output should be consistent with the tool's described functionality."
    )
    tool_mismatch_reasoning: str = Field(
        description="Brief explanation of whether tool outputs are consistent with each tool's expected functionality. Reference specific tool result turns."
    )
    stuck_loops: bool = Field(
        description="Whether the assistant calls the same tool 3+ times with identical or near-identical arguments, getting the same results each time, creating redundant and unrealistic conversation turns."
    )
    stuck_loops_reasoning: str = Field(
        description="Brief explanation of whether stuck loops are present. Reference specific turn indices if found."
    )
    problematic_turn_indices: List[int] = Field(
        default_factory=list,
        description="0-based indices of turns that have quality issues. Empty list if no issues found.",
    )


# ── Evaluator Prompt ──────────────────────────────────────────────────────────

EVALUATOR_SYSTEM_PROMPT = (
    FINDINGS_SUMMARY
    + """

You will be given a synthetic conversation sample. Evaluate it against the criteria above.

IMPORTANT: Focus your evaluation ONLY on the USER role messages. Do NOT penalize
the conversation for unrealistic, inaccurate, or unhelpful assistant responses.
The assistant content is outside the scope of this evaluation. Only evaluate whether
the user's messages read as if written by a real human.

For each criterion, provide:
- A boolean judgment (true/false)
- A brief reasoning string explaining your judgment

Additionally, identify the 0-based indices of any problematic USER turns.
Only include user-role turn indices, never assistant or tool turn indices.

Be strict but fair. Minor stylistic issues are acceptable. Focus on clear violations
of realism in user messages that would make the conversation unusable as training data.
"""
)

EVALUATOR_USER_PROMPT = """Evaluate the following synthetic conversation sample.

Match tag: {match_tag}
User objective (task): {task}
Tools available to assistant: {tools}
Groundtruth tools (correct tools for this task): {gt_tools}

Conversation:
{conversation_text}

Evaluate this conversation for:
a) Overall user message realism (ignore assistant content quality)
b) Pre-tool-call user message realism (ignore assistant content quality)
c) User agent LLM identity leakage
d) Tool simulator schema mismatch
e) Stuck loops (same tool called 3+ times with identical arguments)

Identify any problematic turn indices.
"""

# ── Helper Functions ──────────────────────────────────────────────────────────


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


# ── Main Processing ──────────────────────────────────────────────────────────


def main():
    """Evaluate synthetic conversation quality."""
    parser = argparse.ArgumentParser(description="Evaluate synthetic conversation quality")
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

    # ── Load data ─────────────────────────────────────────────────────────────

    with open(args.input_file, "r") as f:
        samples = json.load(f)
    print(f"Loaded {len(samples)} samples from {args.input_file}")

    # Filter by match_tag if specified
    if args.match_tag_filter != "all":
        samples = [s for s in samples if s.get("match_tag") == args.match_tag_filter]
        print(f"Filtered to {len(samples)} samples with match_tag='{args.match_tag_filter}'")

    # Limit samples if --sample is specified
    if args.sample > 0:
        samples = samples[: args.sample]
        print(f"Limited to first {len(samples)} samples")

    # ── Initialize LLM ───────────────────────────────────────────────────────

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE_URL")
    model_name = "azure/gpt-4o"

    evaluator_llm = ChatOpenAI(
        model=model_name, temperature=0.0, api_key=api_key, base_url=base_url
    ).with_structured_output(ConversationEvaluation)

    # ── Process samples ───────────────────────────────────────────────────────

    results = []
    timing_data = {
        "total_samples": len(samples),
        "evaluated": 0,
        "skipped_no_conversation": 0,
        "evaluation_results": {
            "conversation_realistic": {"pass": 0, "fail": 0},
            "pre_tool_call_realistic": {"pass": 0, "fail": 0},
            "user_identity_leakage": {"detected": 0, "clean": 0},
            "tool_mismatch": {"detected": 0, "clean": 0},
            "stuck_loops": {"detected": 0, "clean": 0},
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

        # Skip samples without conversations
        if not conversation or isinstance(conversation, dict):
            print("  -> Skipped: no valid conversation")
            timing_data["skipped_no_conversation"] += 1
            result_sample = {**sample, "evaluation": None}
            results.append(result_sample)
            continue

        sample_start_time = time.time()

        # ── Step 1: Evaluate ──────────────────────────────────────────────────

        conversation_text = format_conversation_for_eval(conversation)
        eval_user_msg = EVALUATOR_USER_PROMPT.format(
            match_tag=match_tag,
            task=task,
            tools=json.dumps(input_tools),
            gt_tools=json.dumps(gt_tools),
            conversation_text=conversation_text,
        )

        evaluation = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                evaluation = evaluator_llm.invoke(
                    [
                        {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
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

        # Track evaluation stats
        if evaluation.conversation_realistic:
            timing_data["evaluation_results"]["conversation_realistic"]["pass"] += 1
        else:
            timing_data["evaluation_results"]["conversation_realistic"]["fail"] += 1

        if evaluation.pre_tool_call_realistic:
            timing_data["evaluation_results"]["pre_tool_call_realistic"]["pass"] += 1
        else:
            timing_data["evaluation_results"]["pre_tool_call_realistic"]["fail"] += 1

        if evaluation.user_identity_leakage:
            timing_data["evaluation_results"]["user_identity_leakage"]["detected"] += 1
        else:
            timing_data["evaluation_results"]["user_identity_leakage"]["clean"] += 1

        if evaluation.tool_mismatch:
            timing_data["evaluation_results"]["tool_mismatch"]["detected"] += 1
        else:
            timing_data["evaluation_results"]["tool_mismatch"]["clean"] += 1

        if evaluation.stuck_loops:
            timing_data["evaluation_results"]["stuck_loops"]["detected"] += 1
        else:
            timing_data["evaluation_results"]["stuck_loops"]["clean"] += 1

        if args.debug:
            print("  Evaluation:")
            print(f"    conversation_realistic: {evaluation.conversation_realistic}")
            print(f"      -> {evaluation.conversation_realistic_reasoning}")
            print(f"    pre_tool_call_realistic: {evaluation.pre_tool_call_realistic}")
            print(f"      -> {evaluation.pre_tool_call_realistic_reasoning}")
            print(f"    user_identity_leakage: {evaluation.user_identity_leakage}")
            print(f"      -> {evaluation.user_identity_leakage_reasoning}")
            print(f"    tool_mismatch: {evaluation.tool_mismatch}")
            print(f"      -> {evaluation.tool_mismatch_reasoning}")
            print(f"    stuck_loops: {evaluation.stuck_loops}")
            print(f"      -> {evaluation.stuck_loops_reasoning}")
            print(f"    problematic_turns: {evaluation.problematic_turn_indices}")

        # ── Step 2: Build result ──────────────────────────────────────────────

        evaluation_dict = {
            "conversation_realistic": evaluation.conversation_realistic,
            "conversation_realistic_reasoning": evaluation.conversation_realistic_reasoning,
            "pre_tool_call_realistic": evaluation.pre_tool_call_realistic,
            "pre_tool_call_realistic_reasoning": evaluation.pre_tool_call_realistic_reasoning,
            "user_identity_leakage": evaluation.user_identity_leakage,
            "user_identity_leakage_reasoning": evaluation.user_identity_leakage_reasoning,
            "tool_mismatch": evaluation.tool_mismatch,
            "tool_mismatch_reasoning": evaluation.tool_mismatch_reasoning,
            "stuck_loops": evaluation.stuck_loops,
            "stuck_loops_reasoning": evaluation.stuck_loops_reasoning,
            "problematic_turn_indices": evaluation.problematic_turn_indices,
        }

        result_sample = {**sample}
        result_sample["evaluation"] = evaluation_dict

        results.append(result_sample)

        sample_elapsed = time.time() - sample_start_time
        print(f"  -> Done in {sample_elapsed:.2f}s")

        # Save intermediate results
        with open(args.output_file, "w") as f:
            json.dump(results, f, indent=2)

    # ── Final summary ─────────────────────────────────────────────────────────

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
