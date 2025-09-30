"""Streamlit app for Task-Tool matching."""

import json
from pathlib import Path

import streamlit as st

from identity_auth_server.pipelines.task_tool_matcher.task_tool_matcher import TaskToolMatcherFactory
from identity_auth_server.pipelines.task_tool_matcher.types import (
    TaskToolMatcherType,
    TaskToolMatchInput,
    TaskToolMatchOutput,
)


def run_matcher(matcher_type: TaskToolMatcherType, matcher_input: TaskToolMatchInput) -> TaskToolMatchOutput:
    """Run the task-tool matcher."""
    matcher = TaskToolMatcherFactory.create(matcher_type)
    return matcher.match(matcher_input)


# Load MCP server tools
@st.cache_data
def load_mcp_servers_data():
    """Load MCP server tools data."""
    mcp_servers_dir = Path("evaluation/task_tool_matcher/data/mcp_servers")
    mcp_servers_data = {filepath.stem: json.loads(filepath.read_text()) for filepath in mcp_servers_dir.glob("*.json")}
    return mcp_servers_data


mcp_servers_data = load_mcp_servers_data()
mcp_servers_names = list(mcp_servers_data.keys())
matcher_types = {
    "HYBRID": TaskToolMatcherType.HYBRID,
    "EMBEDDINGS": TaskToolMatcherType.EMBEDDINGS,
    "STRUCTURED": TaskToolMatcherType.STRUCTURED,
}

st.title("Task-Tool matcher V0 👋")
st.markdown("This is a playground for testing different versions of the task matcher.")


# MCP server selection
selected_mcp = st.radio(
    "Select one MCP server 👇", options=mcp_servers_names, key="selected_mcp_radio", horizontal=True
)

tool_choice = [tool.get("name", "") for tool in mcp_servers_data[selected_mcp]["tools"]] if selected_mcp else []

# Two columns: left for form, right for tool description
col1, col2 = st.columns([2, 1])
with col1:
    with st.form("matcher_form"):
        requested_tool = st.selectbox(
            "Select a requested tool",
            ["", *tool_choice],
            key="requested_tool_select",
        )
        show_tool_description = st.form_submit_button("Show Tool Description", key="show_tool_description")
        task = st.text_input(
            "Enter a task that requires one tool to be executed👇",
            placeholder="Task",
            key="task_input",
        )
        selected_matcher = st.radio(
            "Select a Matcher 👇", options=list(matcher_types.keys()), key="selected_matcher_radio"
        )
        submitted = st.form_submit_button("Run Matcher", key="submitted")

with col2:
    if st.session_state.get("requested_tool_select"):
        tool_description = [
            tool.get("description", "")
            for tool in mcp_servers_data[selected_mcp]["tools"]
            if selected_mcp and tool["name"] == st.session_state.get("requested_tool_select", "")
        ]
        tool_payload = st.text_area(
            f"Tool name:\n{st.session_state.get('requested_tool_select', '')}",
            value="\n".join(tool_description),
            height=500,
        )

if st.session_state.get("submitted"):
    matcher_input = TaskToolMatchInput(
        task=st.session_state.get("task_input"),
        requested_tool=st.session_state.get("requested_tool_select"),
        mcp_server=mcp_servers_data[st.session_state.get("selected_mcp_radio")],
    )
    result = run_matcher(matcher_types[selected_matcher], matcher_input)
    st.write(result)
