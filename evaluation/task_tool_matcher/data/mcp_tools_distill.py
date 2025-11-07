"""This script loads all MCP server tool information and distills them into a summary."""

import json
import os

from dotenv import dotenv_values
from openai import OpenAI


def clean_tool_description(description: str) -> str:
    """Cleans the tool description by removing certain sections."""
    cut_sequences = [
        "\n    Args:\n",  # for atlassian, hummingbot, paper-search
        "\n\nParameters:\n",  # for nasdaq
        "\n\nIt takes",  # for stripe
    ]
    for seq in cut_sequences:
        if seq in description:
            description = description.split(seq)[0]
    return description


def load_all_tools_as_string(mcp_servers_dir: str) -> str:
    """Loads all tools from MCP server JSON files in a directory and returns them as a single formatted string.

    Args:
        mcp_servers_dir (str): The path to the directory containing the MCP server JSON files.

    Returns:
        str: A string containing all the tool information.
    """
    all_mcp_tools_info = []
    if not os.path.isdir(mcp_servers_dir):
        return f"Error: Directory not found at {mcp_servers_dir}"

    input_files = [os.path.join(mcp_servers_dir, f) for f in os.listdir(mcp_servers_dir) if f.endswith(".json")]

    for file_path in input_files:
        mcp_server_name = os.path.splitext(os.path.basename(file_path))[0]
        with open(file_path, "r") as f:
            mcp_server = json.load(f)
            tools = mcp_server.get("tools", [])

            if not tools:
                continue

            mcp_info_header = f"-- MCP Server: {mcp_server_name} --"

            tools_info_for_mcp = []
            for tool in tools:
                tool_name = tool.get("name", "N/A")
                tool_description = tool.get("description", "")
                cleaned_description = clean_tool_description(tool_description)
                if cleaned_description.endswith("\n"):
                    cleaned_description = cleaned_description.rstrip("\n")

                tool_info = f"*Tool Name:*\n`{tool_name}`\n*Tool Description:*\n`{cleaned_description}`\n"
                tools_info_for_mcp.append(tool_info)

            all_mcp_tools_info.append(mcp_info_header + "\n" + "\n".join(tools_info_for_mcp))

    return "\n\n".join(all_mcp_tools_info)


if __name__ == "__main__":
    mcp_dir = "evaluation/task_tool_matcher/data/mcp_servers"
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # workspace_root = os.path.dirname(script_dir) # assuming apps/ is at the root
    # absolute_mcp_dir = os.path.join(workspace_root, mcp_dir)

    all_tools_string = load_all_tools_as_string(mcp_dir)

    if all_tools_string.startswith("Error:"):
        print(all_tools_string)
    else:
        print(f"Successfully loaded all tool information into a string of length {len(all_tools_string)}.")

        with open("evaluation/task_tool_matcher/data/all_tools.txt", "w") as f:
            f.write(all_tools_string)

    config = dotenv_values()
    client = OpenAI(
        api_key=config.get("OPENAI_API_KEY"),
        base_url=config.get("OPENAI_API_BASE_URL"),
    )

    try:
        system_prompt = (
            "You are an expert in processing MCP tool descriptions. "
            "The user will send you a list of MCPs and their tool descriptions, and your task is to distill and summarize the key functionalities of these tools into a concise format."
        )
        user_prompt = f"""Here is the list of MCP servers and their tools:\n
{all_tools_string}\n\n
Please provide a concise but clear comprehensive summary of the key functionalities of each MCP (do not return anything else)."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        )

        print(response.choices[0].message.content)

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
