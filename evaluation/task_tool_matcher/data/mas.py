"""Multi-Agent System with 3 agents: User, Assistant (with tools), Tool Simulator."""

import argparse
import copy
import json
import os
import time
from collections import defaultdict
from typing import Annotated, Any, Dict, List, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

load_dotenv()

# System prompts for each agent
USER_AGENT_PROMPT = """You are a human user. What you want inherently to achieve is: '{objective}'.
Ask the assistant for help, in the way a human would, jumping straight to the point, you can always trust the assistant.

The assistant might need missing arguments information from you for some tool calling, in this case you need to give that information when asked for it.
If the assistant asks you for anything you do not know or information you do not have, even IDs, then invent it and answer the assistant, just try that what you invent is realistic.
If the assistant asks you for API keys, secrets, or other sensitive information, provide them as if you were a real user, just invent them realistically even though you do not have them.

Respond naturally and directly as a human talking to your assistant, do NOT narrate or describe what's happening, only respond as the human user, you are the human user.
Your response:
"""

USER_EVALUATION_PROMPT = """You are a human user. Your objective: {objective}. The assistant said: {assistant_response}.

Respond naturally as a human would:
- If your objective has been completed by the assistant, then you *MUST* say exactly the words 'thank you'.
- If the assistant asked you a question or needs information, answer it directly.
- If something is unclear or wrong, clarify your request.

Do NOT narrate or describe what's happening, only respond as the human user, you are the human user.
Your response:
"""

USER_EVALUATION_PROMPT_FULL_HISTORY = """You are a human user continuing a conversation with an assistant. Your objective: {objective}

Conversation so far:
{conversation_history}

Respond naturally as the user:
- If your goal is achieved, thank the assistant
- If asked a question, answer it directly
- If something is wrong, clarify
- NEVER say 'thank you' except when:
    * your goal is achieved by the assistant
    * or you are satisfied that your objective is achieved
    * or if the assistant tells you that your goal is achieved then believe it and say 'thank you'.

Your response:
"""

ASSISTANT_AGENT_PROMPT = """You're a helpful AI assistant with tools, your goal is aiding the user.
The user does not want a plan or generic answers, they want you to actually perform the actions, ideally using the tools available to you.

If the user request is missing information needed by a tool required for the user's task, ask for clarifications clearly.
Do not create your own information when you could get that from a tool that matches the task, the tools are perfectly reliable so favor them.
Use the available tools as needed to help the user achieve their goal, the tools are perfect and never make mistakes, trust their answers.

Your response:
"""

SIMULATOR_AGENT_PROMPT = """You are a tool simulator, participating in a conversation between a user and an assistant.
Your objective is to provide realistic tool answers when requested, only providing the answer that a tool would be expected to return.
The conversation so far (you are Tool):
{conversation_history}

Now synthesize the Tool response for the tool: {tool_name} with args: {tool_args}.
Return realistic results that the tool may generate, only creating the necessary data and ensuring results are consistent with the past conversation.
ONLY return the simulated result, do not make *ANY* other comment, do not present do not narrate, only return the tool result as if you are the tool.

Your response:
"""


class AgentState(TypedDict):
    """State dictionary for the multi-agent system workflow."""

    messages: Annotated[Sequence[BaseMessage], "Conversation messages"]
    objective: str
    next_agent: str
    iteration_count: int


class MultiAgentSystem:
    """Multi-agent system with user, assistant, and tool simulator agents."""

    def __init__(self, tools: list[Dict[str, Any]], debug: bool = False, use_full_history: bool = False):
        """Initialize the multi-agent system.

        Args:
            tools: List of tool dictionaries with name, description, and parameters.
            debug: Enable detailed input/output logging for each agent.
            use_full_history: Use full conversation history for user evaluation (vs just last message).
        """
        self.debug = debug
        self.use_full_history = use_full_history
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE_URL")
        model_name = "azure/gpt-4o"

        self.user_llm = ChatOpenAI(model=model_name, temperature=0.7, api_key=api_key, base_url=base_url)
        self.assistant_llm = ChatOpenAI(
            model=model_name, temperature=0.3, api_key=api_key, base_url=base_url
        ).bind_tools(
            [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t.get("parameters", {"type": "object", "properties": {}, "required": []}),
                    },
                }
                for t in tools
            ]
        )
        self.simulator_llm = ChatOpenAI(model=model_name, temperature=0.5, api_key=api_key, base_url=base_url)
        self.graph = self._build_graph()

    def _debug_log(self, agent_name: str, iteration: int, messages_input: list):
        if self.debug:
            print(f"\n{'=' * 120}")
            print(f"[{agent_name.upper()}] Iteration {iteration} - INPUT")
            print(f"{'=' * 120}")
            for i, msg in enumerate(messages_input, 1):
                msg_type = type(msg).__name__
                if hasattr(msg, "content"):
                    print(f"  [{i}] {msg_type}: {msg.content[:600]}{'...' if len(msg.content) > 600 else ''}")
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    print(f"      Tool Calls: {msg.tool_calls}")

    def _debug_log_output(self, agent_name: str, iteration: int, response):
        if self.debug:
            print(f"{'-' * 120}")
            print(f"[{agent_name.upper()}] Iteration {iteration} - OUTPUT")
            if hasattr(response, "content"):
                print(f"  Content: {response.content}")
            if hasattr(response, "tool_calls") and response.tool_calls:
                print(f"  Tool Calls: {response.tool_calls}")
            print(f"{'=' * 120}\n")

    def _user_agent(self, state: AgentState) -> AgentState:
        messages, objective = state["messages"], state["objective"]

        if not messages:
            input_messages = [SystemMessage(content=USER_AGENT_PROMPT.format(objective=objective))]
            self._debug_log("USER AGENT", state["iteration_count"] + 1, input_messages)
            response = self.user_llm.invoke(input_messages)
            self._debug_log_output("USER AGENT", state["iteration_count"] + 1, response)
            return {
                **state,
                "messages": [HumanMessage(content=response.content)],
                "next_agent": "assistant",
                "iteration_count": 1,
            }

        last_msg = messages[-1]
        if isinstance(last_msg, AIMessage) and not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls):
            if self.use_full_history:
                conv_history = "\n".join(
                    [
                        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
                        for m in messages
                        if isinstance(m, (HumanMessage, AIMessage))
                        and not (isinstance(m, AIMessage) and hasattr(m, "tool_calls") and m.tool_calls)
                    ]
                )
                input_messages = [
                    SystemMessage(
                        content=USER_EVALUATION_PROMPT_FULL_HISTORY.format(
                            objective=objective, conversation_history=conv_history
                        )
                    )
                ]
            else:
                input_messages = [
                    SystemMessage(
                        content=USER_EVALUATION_PROMPT.format(objective=objective, assistant_response=last_msg.content)
                    )
                ]

            self._debug_log("USER AGENT", state["iteration_count"] + 1, input_messages)
            response = self.user_llm.invoke(input_messages)
            self._debug_log_output("USER AGENT", state["iteration_count"] + 1, response)
            is_done = any(
                word in response.content.lower() for word in ["thank you", "thanks"]
            )  # , "complete", "perfect", "great"])
            return {
                **state,
                "messages": [*messages, HumanMessage(content=response.content)],
                "next_agent": "end" if is_done else "assistant",
                "iteration_count": state["iteration_count"] + 1,
            }

        return {**state, "next_agent": "assistant"}

    def _assistant_agent(self, state: AgentState) -> AgentState:
        messages = [SystemMessage(content=ASSISTANT_AGENT_PROMPT), *state["messages"]]
        self._debug_log("ASSISTANT AGENT", state["iteration_count"] + 1, messages)
        response = self.assistant_llm.invoke(messages)
        self._debug_log_output("ASSISTANT AGENT", state["iteration_count"] + 1, response)
        next_agent = "simulator" if hasattr(response, "tool_calls") and response.tool_calls else "user"
        return {
            **state,
            "messages": [*state["messages"], response],
            "next_agent": next_agent,
            "iteration_count": state["iteration_count"] + 1,
        }

    def _simulator_agent(self, state: AgentState) -> AgentState:
        last_msg = state["messages"][-1]
        if not (hasattr(last_msg, "tool_calls") and last_msg.tool_calls):
            return {**state, "next_agent": "assistant"}

        full_history_tools = "\n".join(
            [
                f"{'User' if isinstance(m, HumanMessage) else 'Assistant' if isinstance(m, AIMessage) else 'Tool'}: {m.content}"
                for m in state["messages"]
            ]
        )
        results = []
        for tc in last_msg.tool_calls:
            input_messages = [
                SystemMessage(
                    content=SIMULATOR_AGENT_PROMPT.format(
                        conversation_history=full_history_tools, tool_name=tc["name"], tool_args=tc["args"]
                    )
                )
            ]
            self._debug_log("SIMULATOR AGENT", state["iteration_count"] + 1, input_messages)
            sim = self.simulator_llm.invoke(input_messages)
            self._debug_log_output("SIMULATOR AGENT", state["iteration_count"] + 1, sim)
            results.append(ToolMessage(content=sim.content, tool_call_id=tc["id"]))

        return {
            **state,
            "messages": [*state["messages"], *results],
            "next_agent": "assistant",
            "iteration_count": state["iteration_count"] + 1,
        }

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("user", self._user_agent)
        workflow.add_node("assistant", self._assistant_agent)
        workflow.add_node("simulator", self._simulator_agent)
        workflow.set_entry_point("user")

        workflow.add_conditional_edges(
            "user",
            lambda s: "end" if s["next_agent"] == "end" or s["iteration_count"] >= 15 else s["next_agent"],
            {"assistant": "assistant", "end": END},
        )
        workflow.add_conditional_edges(
            "assistant",
            lambda s: "end" if s["iteration_count"] >= 15 else s["next_agent"],
            {"user": "user", "simulator": "simulator", "end": END},
        )
        workflow.add_conditional_edges(
            "simulator",
            lambda s: "end" if s["iteration_count"] >= 15 else s["next_agent"],
            {"assistant": "assistant", "end": END},
        )

        return workflow.compile()

    def run(self, objective: str) -> Dict[str, Any]:
        """Run the multi-agent system with the given objective.

        Args:
            objective: The user's goal that the system should accomplish.

        Returns:
            Final state dictionary with all messages and metadata.

        """
        return self.graph.invoke({"messages": [], "objective": objective, "next_agent": "user", "iteration_count": 0})


def load_synthetic_tasks(file_path: str) -> List[Dict[str, Any]]:
    """Load synthetic tasks from JSON file.

    Args:
        file_path: Path to the synthetic tasks JSON file.

    Returns:
        List of sample dictionaries containing synthetic tasks and metadata.
    """
    with open(file_path, "r") as f:
        return json.load(f)


def load_mcp_server_tools(server_name: str, mcp_dir: str) -> Dict[str, Any]:
    """Load tools from an MCP server JSON file.

    Args:
        server_name: Name of the MCP server.
        mcp_dir: Directory containing MCP server JSON files.

    Returns:
        Dictionary containing server data with tools array.
    """
    file_path = os.path.join(mcp_dir, f"{server_name}.json")
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: MCP server file not found: {file_path}")
        return {"tools": []}


def filter_and_convert_tools(mcp_servers: List[str], tool_names: List[str], mcp_dir: str) -> List[Dict[str, Any]]:
    """Load and filter tools from MCP servers.

    Args:
        mcp_servers: List of MCP server names.
        tool_names: List of tool names to filter.
        mcp_dir: Directory containing MCP server JSON files.

    Returns:
        List of tool dictionaries in MAS format.
    """
    all_tools = []
    print(f"MAS exposed to tools from MCP servers: {mcp_servers}")
    for server_name in set(mcp_servers):
        server_data = load_mcp_server_tools(server_name.replace("-", "_"), mcp_dir)
        for tool in server_data.get("tools", []):
            if tool["name"] in tool_names:
                mas_tool = {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {"type": "object", "properties": {}, "required": []}),
                }
                all_tools.append(mas_tool)
    return all_tools


def convert_messages_to_serializable(messages: List[BaseMessage]) -> List[Dict[str, Any]]:
    """Convert LangChain message objects to JSON-serializable dicts.

    Args:
        messages: List of LangChain message objects.

    Returns:
        List of serializable message dictionaries.
    """
    serializable_messages = []
    for msg in messages:
        msg_dict = {"content": msg.content}

        if isinstance(msg, HumanMessage):
            msg_dict["role"] = "user"
        elif isinstance(msg, AIMessage):
            msg_dict["role"] = "assistant"
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
        elif isinstance(msg, ToolMessage):
            msg_dict["role"] = "tool"
            if hasattr(msg, "tool_call_id"):
                msg_dict["tool_call_id"] = msg.tool_call_id

        serializable_messages.append(msg_dict)

    return serializable_messages


def count_tool_usage(messages: list, tool_names: list) -> int:
    """Count how many unique tools from tool_names were called in the messages."""
    used_tools = {
        tool_call.get("name")
        for message in messages
        if message.get("role") == "assistant"
        for tool_call in message.get("tool_calls", [])
        if tool_call.get("name") in tool_names
    }
    return len(used_tools)


def count_tool_calls(messages: list, tool_names: list) -> int:
    """Count how many tool calls from tool_names were made in the messages."""
    called_tools = [
        tool_call.get("name")
        for message in messages
        if message.get("role") == "assistant"
        for tool_call in message.get("tool_calls", [])
        if tool_call.get("name") in tool_names
    ]
    return len(called_tools)


def immediate_tool_call(messages: list) -> bool:
    """Check if the second message is an assistant tool call."""
    if len(messages) < 2:
        return False
    return messages[1].get("role") == "assistant" and "tool_calls" in messages[1]


def main():
    """Run multi-agent system with synthetic tasks from external file."""
    parser = argparse.ArgumentParser(description="Run MAS with synthetic tasks and dynamic tool loading")
    parser.add_argument("--tasks-file", required=True, help="Path to synthetic tasks JSON file")
    parser.add_argument("--mcp-servers-dir", required=True, help="Path to MCP servers directory")
    parser.add_argument("--output-file", required=True, help="Path for output JSON file")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--use-full-history", action="store_true", help="Use full conversation history")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode (print final conversation)")
    args = parser.parse_args()

    samples = load_synthetic_tasks(args.tasks_file)
    timing_data = {"mcp_servers": [], "total_samples": len(samples)}
    last_mcp_server_name = ""
    mcp_server_start_time = None
    mcp_server_start_idx = -1
    overall_start_time = time.time()
    base_name, ext = os.path.splitext(args.output_file)

    # excluded_server_names = ["atlassian", "azure", "github-official", "grafana", "hummingbot-mcp", "mongodb", "nasdaq-data-link", "notion", "paper-search", "sonarqube", "stripe", "wikipedia-mcp"]
    # excluded_server_names = ["azure", "github-official", "grafana", "hummingbot-mcp", "nasdaq-data-link", "paper-search", "sonarqube", "stripe", "wikipedia-mcp"]
    excluded_server_names = []
    print(f"\n\n~~~ Excluding MCP servers: {excluded_server_names}\n\n")

    for sample_idx, sample in enumerate(samples, 1):
        mcp_server_name = sample["mcp_servers"][0]

        if mcp_server_name in excluded_server_names:
            continue
        if mcp_server_name != last_mcp_server_name:
            results = []
            if mcp_server_start_time is not None:
                elapsed_time = time.time() - mcp_server_start_time
                num_samples = sample_idx - mcp_server_start_idx
                time_per_sample = elapsed_time / num_samples if num_samples > 0 else 0
                print(
                    f"\nFINISHED MCP SERVER: {last_mcp_server_name} in {elapsed_time:.2f} seconds, which is {time_per_sample:.2f} seconds per sample task ({num_samples} samples)!\n"
                )

                timing_data["mcp_servers"].append(
                    {
                        "mcp_server_name": last_mcp_server_name,
                        "num_sample_toolsets": num_samples,
                        "total_time_seconds": elapsed_time,
                        "time_per_sample_seconds": time_per_sample,
                    }
                )
                timing_data["SO_tasks_per_sample"] = sample["SO_tasks_per_sample"]
                timing_data["total_time_seconds"] = time.time() - overall_start_time

                timing_file = f"{base_name}_timing.json"
                with open(timing_file, "w") as f:
                    json.dump(timing_data, f, indent=2)

            last_mcp_server_name = mcp_server_name
            mcp_server_start_time = time.time()
            mcp_server_start_idx = sample_idx

        print(f"\n{'=' * 20} Processing Sample {sample_idx}/{len(samples)} {'=' * 20}")

        tools = filter_and_convert_tools(sample["mcp_servers"], sample["tool_names"], args.mcp_servers_dir)

        if not tools:
            print(f"Warning: No tools found for sample {sample_idx}")
            continue

        mas = MultiAgentSystem(tools=tools, debug=args.debug, use_full_history=args.use_full_history)

        result_sample = copy.deepcopy(sample)
        result_sample["conversation"] = True
        result_sample["conversation_iters"] = []
        result_sample["number_tools_called"] = []
        result_sample["number_tool_calls"] = []
        result_sample["immediate_tool_call"] = []
        result_sample["synthetic_conversations"] = []

        for task_idx, task in enumerate(sample["synthetic_tasks"], 1):
            print(f"\n  Task {task_idx}/{len(sample['synthetic_tasks'])}: {task[:80]}...")

            max_retries = 3
            retry_count = 0
            success = False

            while retry_count < max_retries and not success:
                try:
                    result = mas.run(task)

                    serializable_messages = convert_messages_to_serializable(result["messages"])
                    result_sample["conversation_iters"].append(result["iteration_count"])
                    result_sample["number_tools_called"].append(
                        count_tool_usage(serializable_messages, result_sample["tool_names"])
                    )
                    result_sample["number_tool_calls"].append(
                        count_tool_calls(serializable_messages, result_sample["tool_names"])
                    )
                    result_sample["immediate_tool_call"].append(immediate_tool_call(serializable_messages))
                    result_sample["synthetic_conversations"].append(serializable_messages)

                    print(f"   -> Completed ({result['iteration_count']} iterations)")
                    success = True

                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"    -> Error (retry {retry_count}/{max_retries}): {e}")
                    else:
                        print(f"    -> Error (all {max_retries} retries failed): {e}")
                        result_sample["synthetic_conversations"].append({"error": str(e)})

            if args.verbose:
                print("\n--- Simulated Conversation ---\n")
                for i, msg in enumerate(result["messages"], 1):
                    if isinstance(msg, HumanMessage):
                        print(f"[{i}] APP. USER: {msg.content}")
                    elif isinstance(msg, AIMessage):
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            print(f"[{i}] ASSISTANT: << calls {msg.tool_calls[0]['name']} >>")
                        else:
                            print(f"[{i}] ASSISTANT: {msg.content}")
                    elif isinstance(msg, ToolMessage):
                        print(f"[{i}] SIMULATOR: {msg.content}")

            try:
                tools_called_turnidx = []
                conversations = result_sample.get("synthetic_conversations", [])
                for _, conversation in enumerate(conversations):
                    tools_in_conv = defaultdict(list)
                    for turn_idx, message in enumerate(conversation):
                        if message.get("role") == "assistant" and "tool_calls" in message:
                            tool_calls = message.get("tool_calls", [])
                            for tool_call in tool_calls:
                                tool_name = tool_call.get("name", "N/A")
                                tools_in_conv[tool_name].append(turn_idx)
                    tools_called_turnidx.append(dict(tools_in_conv))

                synthetic_conversations = result_sample.pop("synthetic_conversations", [])
                result_sample["tools_called_turnidx"] = tools_called_turnidx
                result_sample["synthetic_conversations"] = synthetic_conversations
            except Exception as e:
                print(f"    -> Error extracting tools_called_turnidx: {e}")
                result_sample["tools_called_turnidx"] = []

        results.append(result_sample)

        output_file_with_server = f"{base_name}_{mcp_server_name}{ext}"
        with open(output_file_with_server, "w") as f:
            json.dump(results, f, indent=2)
        print(f"   Saved intermediate to {output_file_with_server}")

    if mcp_server_start_time is not None:
        elapsed_time = time.time() - mcp_server_start_time
        num_samples = len(samples) - mcp_server_start_idx + 1
        time_per_sample = elapsed_time / num_samples if num_samples > 0 else 0
        print(
            f"\nFINISHED MCP SERVER: {last_mcp_server_name} in {elapsed_time:.2f} seconds, which is {time_per_sample:.2f} seconds per sample task ({num_samples} samples)!\n"
        )

        timing_data["mcp_servers"].append(
            {
                "mcp_server_name": last_mcp_server_name,
                "num_sample_toolsets": num_samples,
                "total_time_seconds": elapsed_time,
                "time_per_sample_seconds": time_per_sample,
            }
        )

    base_name, ext = os.path.splitext(args.output_file)
    timing_file = f"{base_name}_timing.json"
    with open(timing_file, "w") as f:
        json.dump(timing_data, f, indent=2)
    print(f"\nTiming data saved to: {timing_file}")


if __name__ == "__main__":
    main()
