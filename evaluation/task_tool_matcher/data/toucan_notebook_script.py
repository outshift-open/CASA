"""Script to process the Toucan-1.5M dataset, extract MCP server tool information, and generate synthetic tasks."""

# !uv pip install datasets
import json
import os
import re
from collections import defaultdict
from typing import Any

from datasets import load_dataset

CHINESE_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def contains_chinese(text: str) -> bool:
    """Check if the input text contains Chinese characters."""
    return bool(CHINESE_RE.search(text))


LLM_name = "OSS"
dataset = load_dataset("Agent-Ark/Toucan-1.5M", LLM_name, split="train")


print(f"Number of samples: {len(dataset)}")
print("Sample keys:", dataset[0].keys(), "\n")

print(dataset[0]["subset_name"])
print(dataset[0]["question"])
print(dataset[0]["target_tools"])

# def sample_passes_criteria(sample):
#     try:
#         question_quality_assessment = json.loads(sample["question_quality_assessment"])
#         response_quality_assessment = json.loads(sample["response_quality_assessment"])
#     except json.JSONDecodeError:
#         print("JSONDecodeError for sample:", sample[question_quality_assessment], sample[response_quality_assessment])
#         return False

#     if question_quality_assessment["tool_selection_difficulty"]["score"] < 3:
#         return False
#     if question_quality_assessment["tool_selection_uniqueness"]["score"] < 3:
#         return False
#     if question_quality_assessment["scenario_realism"]["score"] < 3:
#         return False
#     if question_quality_assessment["verifiable"]["score"] < 3:
#         return False

#     if response_quality_assessment["overall_score"] < 3:
#         return False
#     if response_quality_assessment["desired_tools_used_percentage"] < 0.9:
#         return False

#     return True


# filtered_dataset = dataset.filter(sample_passes_criteria)
# print(f"Number of samples after filtering: {len(filtered_dataset)}")

# question_quality_assessment = json.loads(dataset[0]["question_quality_assessment"])
# print(question_quality_assessment["tool_selection_difficulty"]["score"])
# print(question_quality_assessment["tool_selection_uniqueness"]["score"])
# print(question_quality_assessment["scenario_realism"]["score"])
# print(question_quality_assessment["verifiable"]["score"])

# response_quality_assessment = json.loads(dataset[0]["response_quality_assessment"])
# print(response_quality_assessment["overall_score"])
# print(response_quality_assessment["desired_tools_used_percentage"])


datasubset = dataset

MCP_NAME_TO_TOOLS: defaultdict[str, list[dict[str, str]]] = defaultdict(list)

successes = 0
for idx, sample in enumerate(datasubset):
    if len(json.loads(sample["metadata"])["mcp_servers"]) == 1:
        successes += 1
        # print(json.loads(sample["metadata"])["mcp_servers"])

        mcp_server_name = json.loads(sample["metadata"])["mcp_servers"][0]["server_name"]
        mcp_server_name = mcp_server_name.replace("/", "").replace("\\", "").replace(".", "").replace(",", "")

        available_tools = json.loads(sample["available_tools"])
        # print(sample["target_tools"])
        # print(available_tools)
        for i in range(len(available_tools)):
            tool_name = available_tools[i]["function"]["name"]
            tool_description = available_tools[i]["function"]["description"]
            if not any(entry["name"] == tool_name for entry in MCP_NAME_TO_TOOLS[mcp_server_name]):
                MCP_NAME_TO_TOOLS[mcp_server_name].append({"name": tool_name, "description": tool_description})

print("one-mcp tasks: ", successes)
print(len(MCP_NAME_TO_TOOLS.keys()))
total_tools = sum(len(tool_list) for tool_list in MCP_NAME_TO_TOOLS.values())
print(f"Total number of tool entries across all MCPs: {total_tools}")


out_dir = "toucan_mcp_servers"
os.makedirs(out_dir, exist_ok=True)

duplicate = rejected = written = skipped = 0
all_tool_names: list[str] = []
ACCEPTED_MCP_SERVERS = defaultdict(list)

for mcp_name, tools in MCP_NAME_TO_TOOLS.items():
    path = os.path.join(out_dir, f"{mcp_name}.json")

    reject = False
    # filter on Chinese characters and missing descriptions
    for tool in tools:
        if tool["description"] is None or contains_chinese(tool["name"]) or contains_chinese(tool["description"]):
            reject = True
            rejected += 1

    # filter on duplicate tool names
    for tool in tools:
        if tool["name"] in all_tool_names:
            print(f"  Skipping {mcp_name} due to duplicate tool name: {tool['name']}")
            reject = True
            rejected += 1
            duplicate += 1
            break

    if reject:
        print(f"  Skipping {mcp_name} due to Chinese characters or missing descriptions.")
        continue

    ACCEPTED_MCP_SERVERS[mcp_name] = tools

    data = {"name": mcp_name, "tools": tools}
    serialized = json.dumps(data, ensure_ascii=False, indent=2)

    # track all unique tool names so far
    all_tool_names.extend(tool["name"] for tool in tools)

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                if f.read().strip() == serialized:
                    skipped += 1
                    continue
        except Exception:
            pass

    with open(path, "w", encoding="utf-8") as f:
        f.write(serialized)
    written += 1

print(
    f"JSON export complete. Written: {written}, skipped (unchanged): {skipped}, rejected: {rejected}, duplicate: {duplicate}, total: {written + skipped + rejected + duplicate}"
)
print(len(ACCEPTED_MCP_SERVERS), "MCP servers accepted.")

datasubset = dataset.select(range(40000))
print(f"Number of samples scanned: {len(datasubset)}")

generated_samples: list[list[dict[str, Any]]] = [[] for _ in range(3)]
used_mcps = set()
for idx, sample in enumerate(datasubset):
    if len(json.loads(sample["metadata"])["mcp_servers"]) == 1:
        mcp_server_name = json.loads(sample["metadata"])["mcp_servers"][0]["server_name"]
        mcp_server_name = mcp_server_name.replace("/", "").replace("\\", "").replace(".", "").replace(",", "")
        if mcp_server_name in ACCEPTED_MCP_SERVERS:
            synthetic_task = sample["question"]
            tool_names = sample["target_tools"].split(", ")

            if len(generated_samples[len(tool_names) - 1]) < 1100:
                mcp_servers = [mcp_server_name for _ in tool_names]

                if len(ACCEPTED_MCP_SERVERS[mcp_server_name]) >= 2 * len(tool_names):
                    task_sample = {
                        "tool_names": tool_names,
                        "mcp_servers": mcp_servers,
                        "synthetic_tasks": [synthetic_task],
                        "system_prompt": f"toucan_{LLM_name}_mcp",
                        "tools_per_task": len(tool_names),
                        "SO_tasks_per_sample": 1,
                        "conversation": False,
                    }
                    used_mcps.add(mcp_server_name)
                    generated_samples[len(tool_names) - 1].append(task_sample)

for i in range(3):
    print(f"Number of {i + 1}-tool tasks: {len(generated_samples[i])}")
    output_path = f"toucan_{LLM_name}_1mcptasks_{i + 1}tool.json"
    with open(output_path, "w") as f:
        json.dump(generated_samples[i], f, indent=2)
    print(f"{len(generated_samples[i])} tasks, saved to {output_path}")
print(f"Used {len(used_mcps)} MCPs:", used_mcps)


for filename in os.listdir(out_dir):
    mcp_name = os.path.splitext(filename)[0]
    if mcp_name not in used_mcps:
        file_path = os.path.join(out_dir, filename)
        os.remove(file_path)
        print(f"Deleted: {file_path}")


for mcp_name in used_mcps:
    print(f'"{mcp_name}",')
