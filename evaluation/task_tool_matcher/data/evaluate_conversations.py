"""Conversation Quality Evaluator.

Reads MAS output samples and evaluates each conversation for realism and identity
leakage using an LLM with structured outputs.
"""

import argparse
import copy
import json
import os
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

2. STUCK LOOPS: The assistant and the user repeat identical or near-identical messages in a
    loop getting the same responses each time, creating redundant and unrealistic conversation turns."

Important: Focus the evaluation only up to **BEFORE THE FIRST TOOL CALL**, everything after
the first tool call (including the call itself) is outside the scope of this evaluation.
"""


class ConversationEvaluation(BaseModel):
    """Structured evaluation of a single synthetic conversation."""

    # conversation_realistic: bool = Field(
    #     description="Whether ALL user messages throughout the conversation read as realistic human utterances. Ignore assistant message quality entirely — only evaluate whether user turns sound like a real person. Consider natural phrasing, coherent responses to the assistant, and absence of LLM-like language."
    # )
    # conversation_realistic_reasoning: str = Field(
    #     description="Brief explanation of why user messages are or are not realistic. Reference specific user turns only."
    # )
    pre_tool_call_realistic: bool = Field(
        description="Whether user messages UP TO AND INCLUDING the first tool call are realistic. If there are no tool calls, evaluate all user messages. Focus only on whether the user's request and follow-up messages sound like a real human — ignore the assistant's tool selection or responses."
    )
    pre_tool_call_realistic_reasoning: str = Field(
        description="Brief explanation of why the user messages in the pre-tool-call portion are or are not realistic. Reference specific user turns only."
    )
    user_identity_leakage: bool = Field(
        description="Whether the USER agent reveals it is an LLM at any point **BEFORE THE FIRST TOOL CALL**. Look for phrases like 'I am trained on...', 'As an AI...', overly formal/robotic language, unsolicited technical disclaimers, or any other phrasing that a real human would never use when asking for help."
    )
    user_identity_leakage_reasoning: str = Field(
        description="Brief explanation of whether and where user identity leakage occurs. Quote the specific problematic text if found."
    )
    # tool_mismatch: bool = Field(
    #     description="Whether the tool simulator returns data that does not match what the called tool would logically produce given its purpose and schema. For example, a weather tool returning database query results, or a file search tool returning financial data. The tool output should be consistent with the tool's described functionality."
    # )
    # tool_mismatch_reasoning: str = Field(
    #     description="Brief explanation of whether tool outputs are consistent with each tool's expected functionality. Reference specific tool result turns."
    # )
    stuck_loops: bool = Field(
        description="Whether the assistant and the user repeat identical or near-identical messages in a loop at any point **BEFORE THE TOOL CALL**, getting the same responses each time, creating redundant and unrealistic conversation turns."
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

Label: {match_tag}
User objective (task): {task}
Tool under evaluation: {tool}
Groundtruth seed tool: {gt_tool}

Conversation:
{conversation_text}

Evaluate this conversation for:
a) Pre-tool-call user message realism (ignore assistant content quality)
b) User agent LLM identity leakage
c) Stuck loops (same exchanges repeated creating redundant turns)

Identify any problematic turn indices.
"""

# ── Helper Functions ──────────────────────────────────────────────────────────


def find_first_tool_call_index(conversation: List[Dict[str, Any]]) -> int | None:
    """Return the 0-based index of the first turn that contains a tool call, or None."""
    for i, turn in enumerate(conversation):
        if turn.get("tool_calls"):
            return i
    return None


def format_conversation_for_eval(conversation: List[Dict[str, Any]]) -> str:
    """Format a conversation into readable text for evaluation."""
    lines = []
    for i, turn in enumerate(conversation):
        role = turn.get("role", "unknown").upper()
        content = turn.get("content", "")
        tool_calls = turn.get("tool_calls", [])

        if tool_calls:
            tool_names = [tc.get("function", {}).get("name", "unknown") for tc in tool_calls]
            lines.append(f"[{i}] {role}: {content}")
            lines.append(f"     << calls tools: {', '.join(tool_names)} >>")
        elif role == "TOOL":
            tool_id = turn.get("tool_call_id", "N/A")
            content_preview = content[:200] + "..." if len(content) > 200 else content
            lines.append(f"[{i}] {role} (call_id={tool_id}): {content_preview}")
        else:
            lines.append(f"[{i}] {role}: {content}")
    return "\n".join(lines)


def get_nested(data: Dict[str, Any], *keys: str) -> Any:
    """Safely traverse nested dictionaries."""
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def extract_sample_context(sample: Dict[str, Any]) -> Dict[str, Any]:
    """Extract evaluation context across dataset variants."""
    request = sample.get("request", {})
    metadata = sample.get("metadata", {})

    seed_task_req = get_nested(metadata, "request", "conversation", "seed_task_request") or {}
    task_tool_request = seed_task_req.get("task_tool_request") or {}
    task_seed_tool = seed_task_req.get("task_seed_tool") or {}

    input_tool = request.get("tool") or task_tool_request.get("tool") or {}
    conversation = get_nested(request, "conversation", "messages")

    return {
        "request": request,
        "metadata": metadata,
        "conversation": conversation,
        "task": task_tool_request.get("task", ""),
        "input_tool": input_tool,
        "gt_tool": task_seed_tool,
    }


# ── Main Processing ──────────────────────────────────────────────────────────


def main():
    """Evaluate synthetic conversation quality."""
    parser = argparse.ArgumentParser(description="Evaluate synthetic conversation quality")
    parser.add_argument("--input-file", required=True, help="Path to MAS output JSON file")
    parser.add_argument("--output-file", required=True, help="Path for output JSON file with evaluations")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--sample", type=int, default=0, help="Only process N samples (0 = all)")
    parser.add_argument(
        "--model",
        choices=["4o", "52"],
        default="NaN",
        help="LLM model to use: '4o' for GPT-4o, '52' for GPT-5.2 (default: NaN)",
    )
    parser.add_argument(
        "--label-filter",
        choices=["relevant", "irrelevant", "all"],
        default="all",
        help="Only process samples with this label (default: all)",
    )
    args = parser.parse_args()

    # ── Load data ─────────────────────────────────────────────────────────────

    with open(args.input_file, "r") as f:
        samples = json.load(f)
    print(f"Loaded {len(samples)} samples from {args.input_file}")

    # Filter by label if specified
    if args.label_filter != "all":
        is_relevant = args.label_filter == "relevant"
        samples = [s for s in samples if s.get("label", {}).get("relevant") == is_relevant]
        print(f"Filtered to {len(samples)} samples with label='{args.label_filter}'")

    # Limit samples if --sample is specified
    if args.sample > 0:
        samples = samples[: args.sample]
        print(f"Limited to first {len(samples)} samples")

    # ── Initialize LLM ───────────────────────────────────────────────────────

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE_URL")
    model_name_map = {"4o": "azure/gpt-4o", "52": "azure/gpt-5.2"}
    model_name = model_name_map[args.model]

    evaluator_llm = ChatOpenAI(
        model=model_name, temperature=1.0, api_key=api_key, base_url=base_url
    ).with_structured_output(ConversationEvaluation)

    # ── Process samples ───────────────────────────────────────────────────────

    results = []

    for sample_idx, sample in enumerate(samples, 1):
        is_relevant = sample.get("label", {}).get("relevant", True)
        match_tag = "relevant" if is_relevant else "irrelevant"
        sample_context = extract_sample_context(sample)
        conversation = sample_context["conversation"]
        task = sample_context["task"]
        input_tool = sample_context["input_tool"]
        gt_tool = sample_context["gt_tool"]

        print(f"\n{'=' * 20} Evaluating Sample {sample_idx}/{len(samples)} [{match_tag}] {'=' * 20}")
        print(f"  Task: {task[:80]}...")

        # Skip samples without conversations
        if not isinstance(conversation, list) or not conversation:
            print(f"  -> Skipped: no valid conversation messages ({type(conversation).__name__})")
            results.append(sample)
            continue

        # ── Step 1: Evaluate ──────────────────────────────────────────────────

        conversation_text = format_conversation_for_eval(conversation)
        eval_user_msg = EVALUATOR_USER_PROMPT.format(
            match_tag=match_tag,
            task=task,
            tool=json.dumps(input_tool),
            gt_tool=json.dumps(gt_tool),
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
            results.append(sample)
            continue

        if args.debug:
            print("  Evaluation:")
            print(f"    pre_tool_call_realistic: {evaluation.pre_tool_call_realistic}")
            print(f"      -> {evaluation.pre_tool_call_realistic_reasoning}")
            print(f"    user_identity_leakage: {evaluation.user_identity_leakage}")
            print(f"      -> {evaluation.user_identity_leakage_reasoning}")
            print(f"    stuck_loops: {evaluation.stuck_loops}")
            print(f"      -> {evaluation.stuck_loops_reasoning}")
            print(f"    problematic_turns: {evaluation.problematic_turn_indices}")

        # ── Step 2: Build result ──────────────────────────────────────────────

        first_tool_idx = find_first_tool_call_index(conversation)
        problematic_before_tool_call = (
            any(idx < first_tool_idx for idx in evaluation.problematic_turn_indices)
            if first_tool_idx is not None and evaluation.problematic_turn_indices
            else False
        )

        conversation_quality_check = {
            "pre_tool_call_realistic": {
                "reason": evaluation.pre_tool_call_realistic_reasoning,
                "result": evaluation.pre_tool_call_realistic,
            },
            "user_identity_leakage": {
                "reason": evaluation.user_identity_leakage_reasoning,
                "result": evaluation.user_identity_leakage,
            },
            "stuck_loops": {
                "reason": evaluation.stuck_loops_reasoning,
                "result": evaluation.stuck_loops,
            },
            "problematic_turn_indices": evaluation.problematic_turn_indices,
            "problematic_before_tool_call": problematic_before_tool_call,
        }

        result_sample = copy.deepcopy(sample)
        curation = (
            result_sample.setdefault("metadata", {})
            .setdefault("request", {})
            .setdefault("conversation", {})
            .setdefault("curation_metadata", {})
        )
        curation["conversation_quality_check"] = conversation_quality_check

        results.append(result_sample)

        # Save intermediate results
        with open(args.output_file, "w") as f:
            json.dump(results, f, indent=2)

    # ── Final summary ─────────────────────────────────────────────────────────

    print(f"\n{'=' * 60}")
    print(f"COMPLETED: {len(results)} samples processed")
    print(f"Results saved to: {args.output_file}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
