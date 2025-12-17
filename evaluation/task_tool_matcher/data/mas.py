"""Multi-Agent System with 3 agents: User, Assistant (with tools), Tool Simulator."""

import os
from typing import Annotated, Any, Dict, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

load_dotenv()

# System prompts for each agent
USER_AGENT_PROMPT = """You are a human user. What you want inherently: '{objective}'.
Ask the assistant for help in the way a human would, jumping straight to the point.
The assistant might need more information from you to carry out your request, for example some missing arguments needed for some tool calling, in this case you need to give that information."""

USER_EVALUATION_PROMPT = """You are a human user. Your objective: {objective}. The assistant said: {assistant_response}.

Respond naturally as a human would:
- If your objective has been completed by the assistant, then you *MUST* say exactly the words 'thank you'.
- If the assistant asked you a question or needs information, answer it directly.
- If something is unclear or wrong, clarify your request.

Do NOT narrate or describe what's happening - just respond as the human user, you are the human user."""

USER_EVALUATION_PROMPT_FULL_HISTORY = """You are a human user continuing a conversation with an assistant. Your objective: {objective}

Conversation so far:
{conversation_history}

Respond naturally as the user:
- If your goal is achieved, thank the assistant
- If asked a question, answer it directly
- If something is wrong, clarify
- NEVER say 'thank you' unless your goal is achieved by the assistant

Your response:"""

ASSISTANT_AGENT_PROMPT = """You're a helpful AI assistant with tools, your goal is aiding the user.
If the user request is missing information needed by a tool required for the user's task, ask for clarifications clearly."""

SIMULATOR_AGENT_PROMPT = """Simulate the tool: {tool_name} with args: {tool_args}.
Return realistic results that the tool may generate, only creating the necessary data.
Keep consistency across multiple calls to the same tool within the same conversation."""


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
        model_name = "gpt-4o"

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

        results = []
        for tc in last_msg.tool_calls:
            input_messages = [
                HumanMessage(content=SIMULATOR_AGENT_PROMPT.format(tool_name=tc["name"], tool_args=tc["args"]))
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


def main():
    """Example usage of the multi-agent system."""
    tools = [
        {
            "name": "schedule_meeting",
            "description": "Schedule a meeting",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"},
                    "time": {"type": "string"},
                    "participants": {"type": "string"},
                },
                "required": ["date", "time", "participants"],
            },
        }
    ]

    mas = MultiAgentSystem(tools=tools, debug=True, use_full_history=True)
    root_intent = "Schedule a team meeting Wednesday with Ben, Chiara, and myself"
    result = mas.run(root_intent)

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


if __name__ == "__main__":
    main()
