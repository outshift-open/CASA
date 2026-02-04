"""Generate a comprehensive visual diagram of the Multi-Agent System (MAS) workflow.

This script creates 5 iterations of the diagram, each improving on the previous.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

# Modern dark color palette - IMPROVED CONTRAST
COLORS = {
    "bg": "#0d1117",
    "user": "#1a5c2c",  # Darker green for boxes
    "user_light": "#7ee787",  # Bright green for text
    "assistant": "#5a3d8a",  # Darker purple for boxes
    "assistant_light": "#d2a8ff",  # Bright purple for text
    "simulator": "#1158a0",  # Darker blue for boxes
    "simulator_light": "#79c0ff",  # Bright blue for text
    "arrow": "#c9d1d9",  # Brighter arrow color
    "text": "#ffffff",  # Pure white for main text
    "text_dark": "#0d1117",
    "highlight": "#f0b429",  # Brighter gold
    "success": "#3fb950",
    "error": "#ff7b72",  # Brighter red
    "border": "#484f58",  # Brighter border
    "card_bg": "#161b22",
    "mcp": "#ffa657",  # Brighter orange
    "input": "#79c0ff",
    "output": "#7ee787",
}


def draw_rounded_box(ax, x, y, w, h, color, edge_color, alpha=0.95, lw=2.5, radius=0.3):
    """Draw a rounded rectangle."""
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        facecolor=color,
        edgecolor=edge_color,
        linewidth=lw,
        alpha=alpha,
    )
    ax.add_patch(box)
    return box


def draw_agent(ax, x, y, w, h, color, light_color, letter, name, desc_lines, llm_info):
    """Draw an agent box with header, icon, and description."""
    # Shadow
    draw_rounded_box(ax, x + 0.1, y - 0.1, w, h, "black", "none", alpha=0.3, lw=0)
    # Main box
    draw_rounded_box(ax, x, y, w, h, color, light_color, alpha=0.95, lw=3)
    # Header highlight
    draw_rounded_box(ax, x, y + h - 1.2, w, 1.2, light_color, "none", alpha=0.25, lw=0)

    # Icon circle
    circle = Circle((x + 0.7, y + h - 0.6), 0.4, facecolor=light_color, edgecolor="white", lw=2)
    ax.add_patch(circle)
    ax.text(
        x + 0.7,
        y + h - 0.6,
        letter,
        fontsize=22,
        ha="center",
        va="center",
        color=COLORS["text_dark"],
        fontweight="bold",
        family="monospace",
    )

    # Name - LARGER FONT
    ax.text(x + 1.4, y + h - 0.6, name, fontsize=18, fontweight="bold", color=COLORS["text"], va="center")

    # Description lines - LARGER FONT, BRIGHTER COLOR
    for i, line in enumerate(desc_lines):
        ax.text(x + 0.3, y + h - 1.7 - i * 0.5, line, fontsize=12, color=COLORS["text"], alpha=0.95)

    # LLM info at bottom - LARGER FONT
    ax.text(
        x + w / 2,
        y + 0.4,
        llm_info,
        fontsize=10,
        ha="center",
        va="center",
        color=light_color,
        family="monospace",
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.15", facecolor=COLORS["bg"], edgecolor=light_color, alpha=0.95, lw=1.5),
    )


def draw_arrow(ax, start, end, color, curved=0, label=None, lw=2.5):
    """Draw an arrow with optional label."""
    if curved != 0:
        style = f"arc3,rad={curved}"
        arrow = FancyArrowPatch(
            start, end, connectionstyle=style, arrowstyle="-|>", mutation_scale=20, color=color, linewidth=lw, alpha=0.9
        )
    else:
        arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=20, color=color, linewidth=lw, alpha=0.9)
    ax.add_patch(arrow)

    if label:
        mid_x = (start[0] + end[0]) / 2 + (curved * 1.5 if curved else 0)
        mid_y = (start[1] + end[1]) / 2
        ax.text(
            mid_x,
            mid_y,
            label,
            fontsize=12,
            ha="center",
            va="center",
            color=COLORS["text"],
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS["bg"], edgecolor=color, alpha=0.98, linewidth=2),
        )


def draw_state_node(ax, x, y, label, color, is_terminal=False):
    """Draw a state machine node."""
    if is_terminal:
        circle = Circle((x, y), 0.55, facecolor=color, edgecolor="white", lw=3)
        ax.add_patch(circle)
        ax.text(
            x, y, label, fontsize=11, ha="center", va="center", color="white", fontweight="bold", family="monospace"
        )
    else:
        draw_rounded_box(ax, x - 1, y - 0.5, 2, 1, color, "white", lw=3, radius=0.18)
        ax.text(x, y, label, fontsize=14, ha="center", va="center", color="white", fontweight="bold")


def draw_info_panel(ax, x, y, w, h, title, items, title_color, border_color):
    """Draw an information panel with bullet points."""
    draw_rounded_box(ax, x, y, w, h, COLORS["bg"], border_color, alpha=0.95, lw=2.5)
    ax.text(x + 0.3, y + h - 0.4, title, fontsize=14, fontweight="bold", color=title_color)
    for i, (text, color) in enumerate(items):
        ax.text(x + 0.3, y + h - 0.9 - i * 0.45, f"• {text}", fontsize=11, color=color, fontweight="bold")


def create_iteration_1():
    """Iteration 1: Premium quality with maximum readability."""
    # Balanced canvas - figsize 36x30 with coordinate system 52x44 gives good font proportions
    fig, ax = plt.subplots(1, 1, figsize=(36, 30))
    ax.set_xlim(0, 52)
    ax.set_ylim(0, 44)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    # === TITLE ===
    ax.text(
        26,
        43.0,
        "Conversation-Simulation MAS Overview",
        fontsize=64,
        fontweight="bold",
        ha="center",
        va="center",
        color=COLORS["text"],
    )
    ax.text(
        26,
        41.0,
        "LangGraph-based Multi-Agent System for Task-Tool Matcher Evaluation",
        fontsize=30,
        ha="center",
        va="center",
        color=COLORS["arrow"],
        style="italic",
    )
    ax.plot([2, 50], [39.8, 39.8], color=COLORS["assistant_light"], linewidth=3, alpha=0.6)

    # === DATA PIPELINE ===
    ax.text(26, 38.2, "DATA PIPELINE", fontsize=44, fontweight="bold", ha="center", color=COLORS["text"])

    pipeline_y = 35.2
    box_w = 7.5
    box_h = 4.0
    pipeline = [
        (6, "INPUT", "tasks.json +\nMCP servers", COLORS["input"]),
        (16, "LOAD", "filter_and_\nconvert_tools()", COLORS["mcp"]),
        (26, "EXECUTE", "MultiAgentSystem\n.run(objective)", COLORS["assistant_light"]),
        (36, "SERIALIZE", "convert_to_\nserializable()", COLORS["simulator_light"]),
        (46, "OUTPUT", "JSON Results\n+ Metrics", COLORS["output"]),
    ]

    for px, title, desc, color in pipeline:
        draw_rounded_box(
            ax,
            px - box_w / 2,
            pipeline_y - box_h / 2,
            box_w,
            box_h,
            COLORS["card_bg"],
            color,
            alpha=0.95,
            lw=4,
            radius=0.3,
        )
        ax.text(px, pipeline_y + 0.9, title, fontsize=32, ha="center", va="center", color=color, fontweight="bold")
        ax.text(
            px, pipeline_y - 0.7, desc, fontsize=20, ha="center", va="center", color=COLORS["text"], family="monospace"
        )

    for i in range(len(pipeline) - 1):
        start_x = pipeline[i][0] + box_w / 2 + 0.3
        end_x = pipeline[i + 1][0] - box_w / 2 - 0.3
        ax.annotate(
            "",
            xy=(end_x, pipeline_y),
            xytext=(start_x, pipeline_y),
            arrowprops=dict(arrowstyle="-|>", color=COLORS["arrow"], lw=5, mutation_scale=25),
        )

    # === CORE AGENTS ===
    ax.text(26, 31.5, "CORE AGENTS", fontsize=44, fontweight="bold", ha="center", color=COLORS["text"])

    agent_y = 20.0
    agent_h = 10.0
    agent_w = 12.0

    # Positions with generous gaps for arrows
    user_x = 2
    asst_x = 20
    tool_x = 38

    # User Agent
    draw_rounded_box(ax, user_x, agent_y, agent_w, agent_h, COLORS["user"], COLORS["user_light"], alpha=0.95, lw=4)
    ax.add_patch(plt.Circle((user_x + 1.2, agent_y + agent_h - 1.2), 0.85, color=COLORS["user_light"], zorder=10))
    ax.text(
        user_x + 1.2,
        agent_y + agent_h - 1.2,
        "U",
        fontsize=36,
        ha="center",
        va="center",
        color=COLORS["user"],
        fontweight="bold",
        zorder=11,
    )
    ax.text(
        user_x + 2.8,
        agent_y + agent_h - 1.2,
        "User Agent",
        fontsize=36,
        fontweight="bold",
        va="center",
        color=COLORS["user_light"],
    )

    user_desc = ["Simulates realistic", "human behavior", "Can be vague initially", 'Says "thank you" → END']
    for i, line in enumerate(user_desc):
        ax.text(user_x + 0.6, agent_y + agent_h - 3.2 - i * 1.3, line, fontsize=24, color=COLORS["text"])
    ax.text(
        user_x + 0.6,
        agent_y + 0.7,
        "ChatOpenAI | temp=0.7",
        fontsize=20,
        color=COLORS["user_light"],
        style="italic",
        family="monospace",
    )

    # Assistant Agent
    draw_rounded_box(
        ax, asst_x, agent_y, agent_w, agent_h, COLORS["assistant"], COLORS["assistant_light"], alpha=0.95, lw=4
    )
    ax.add_patch(plt.Circle((asst_x + 1.2, agent_y + agent_h - 1.2), 0.85, color=COLORS["assistant_light"], zorder=10))
    ax.text(
        asst_x + 1.2,
        agent_y + agent_h - 1.2,
        "A",
        fontsize=36,
        ha="center",
        va="center",
        color=COLORS["assistant"],
        fontweight="bold",
        zorder=11,
    )
    ax.text(
        asst_x + 2.8,
        agent_y + agent_h - 1.2,
        "Assistant Agent",
        fontsize=36,
        fontweight="bold",
        va="center",
        color=COLORS["assistant_light"],
    )

    asst_desc = ["AI with tool access", "Processes requests", "Invokes tool_calls[]", "Uses ask_user tool"]
    for i, line in enumerate(asst_desc):
        ax.text(asst_x + 0.6, agent_y + agent_h - 3.2 - i * 1.3, line, fontsize=24, color=COLORS["text"])
    ax.text(
        asst_x + 0.6,
        agent_y + 0.7,
        "ChatOpenAI | temp=0.3",
        fontsize=20,
        color=COLORS["assistant_light"],
        style="italic",
        family="monospace",
    )

    # Tool Simulator Agent
    draw_rounded_box(
        ax, tool_x, agent_y, agent_w, agent_h, COLORS["simulator"], COLORS["simulator_light"], alpha=0.95, lw=4
    )
    ax.add_patch(plt.Circle((tool_x + 1.2, agent_y + agent_h - 1.2), 0.85, color=COLORS["simulator_light"], zorder=10))
    ax.text(
        tool_x + 1.2,
        agent_y + agent_h - 1.2,
        "T",
        fontsize=36,
        ha="center",
        va="center",
        color=COLORS["simulator"],
        fontweight="bold",
        zorder=11,
    )
    ax.text(
        tool_x + 2.8,
        agent_y + agent_h - 1.2,
        "Simulator Agent",
        fontsize=36,
        fontweight="bold",
        va="center",
        color=COLORS["simulator_light"],
    )

    tool_desc = ["Generates tool outputs", "Full context aware", "No actual API calls", "Returns ToolMessage"]
    for i, line in enumerate(tool_desc):
        ax.text(tool_x + 0.6, agent_y + agent_h - 3.2 - i * 1.3, line, fontsize=24, color=COLORS["text"])
    ax.text(
        tool_x + 0.6,
        agent_y + 0.7,
        "ChatOpenAI | temp=0.5",
        fontsize=20,
        color=COLORS["simulator_light"],
        style="italic",
        family="monospace",
    )

    # === AGENT ARROWS ===
    user_right = user_x + agent_w  # 15
    asst_left = asst_x  # 20
    asst_right = asst_x + agent_w  # 33
    tool_left = tool_x  # 38

    arrow_y_top = 27.0
    arrow_y_bot = 23.0

    gap1_center = (user_right + asst_left) / 2  # 17.5
    gap2_center = (asst_right + tool_left) / 2  # 35.5

    # User → Assistant (HumanMessage)
    ax.annotate(
        "",
        xy=(asst_left - 0.3, arrow_y_top),
        xytext=(user_right + 0.3, arrow_y_top),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["user_light"], lw=6, mutation_scale=30),
    )
    ax.text(
        gap1_center,
        arrow_y_top + 0.5,
        "HumanMessage",
        fontsize=28,
        ha="center",
        va="bottom",
        color=COLORS["user_light"],
        fontweight="bold",
    )

    # Assistant → Tool (tool_calls)
    ax.annotate(
        "",
        xy=(tool_left - 0.3, arrow_y_top),
        xytext=(asst_right + 0.3, arrow_y_top),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["assistant_light"], lw=6, mutation_scale=30),
    )
    ax.text(
        gap2_center,
        arrow_y_top + 0.5,
        "tool_calls",
        fontsize=28,
        ha="center",
        va="bottom",
        color=COLORS["assistant_light"],
        fontweight="bold",
    )

    # Tool → Assistant (ToolMessage)
    ax.annotate(
        "",
        xy=(asst_right + 0.3, arrow_y_bot),
        xytext=(tool_left - 0.3, arrow_y_bot),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["simulator_light"], lw=6, mutation_scale=30),
    )
    ax.text(
        gap2_center,
        arrow_y_bot - 0.5,
        "ToolMessage",
        fontsize=28,
        ha="center",
        va="top",
        color=COLORS["simulator_light"],
        fontweight="bold",
    )

    # Assistant → User (AIMessage)
    ax.annotate(
        "",
        xy=(user_right + 0.3, arrow_y_bot),
        xytext=(asst_left - 0.3, arrow_y_bot),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["assistant_light"], lw=6, mutation_scale=30),
    )
    ax.text(
        gap1_center,
        arrow_y_bot - 0.5,
        "AIMessage",
        fontsize=28,
        ha="center",
        va="top",
        color=COLORS["assistant_light"],
        fontweight="bold",
    )

    # === STATE MACHINE ===
    draw_rounded_box(ax, 2, 4.8, 48, 14.5, COLORS["card_bg"], COLORS["highlight"], alpha=0.85, lw=4)
    ax.text(26, 18.5, "LangGraph State Machine", fontsize=40, fontweight="bold", ha="center", color=COLORS["highlight"])

    node_y = 13.0
    node_r = 1.2

    # State nodes - with "agent" in labels
    ax.add_patch(plt.Circle((6, node_y), node_r, color=COLORS["highlight"], zorder=10))
    ax.text(6, node_y, "START", fontsize=24, ha="center", va="center", color="white", fontweight="bold", zorder=11)

    draw_rounded_box(ax, 11, node_y - 1.1, 6, 2.2, COLORS["user"], "white", lw=4, radius=0.3)
    ax.text(14, node_y, "user agent", fontsize=26, ha="center", va="center", color="white", fontweight="bold")

    draw_rounded_box(ax, 20, node_y - 1.1, 9, 2.2, COLORS["assistant"], "white", lw=4, radius=0.3)
    ax.text(24.5, node_y, "assistant agent", fontsize=26, ha="center", va="center", color="white", fontweight="bold")

    draw_rounded_box(ax, 32, node_y - 1.1, 9, 2.2, COLORS["simulator"], "white", lw=4, radius=0.3)
    ax.text(36.5, node_y, "simulator agent", fontsize=26, ha="center", va="center", color="white", fontweight="bold")

    ax.add_patch(plt.Circle((46, node_y), node_r, color=COLORS["error"], zorder=10))
    ax.text(46, node_y, "END", fontsize=24, ha="center", va="center", color="white", fontweight="bold", zorder=11)

    # === SYSTEM PROMPT INFO BELOW EACH NODE ===
    info_y = node_y - 3.5
    info_font = 18

    # User agent info
    ax.text(
        14,
        info_y + 0.6,
        "System Prompt Inputs:",
        fontsize=info_font + 1,
        ha="center",
        color=COLORS["user_light"],
        fontweight="bold",
    )
    ax.text(14, info_y - 0.1, "objective", fontsize=info_font, ha="center", color=COLORS["text"], family="monospace")
    ax.text(
        14,
        info_y - 0.7,
        "Regular: last_msg only",
        fontsize=info_font - 2,
        ha="center",
        color=COLORS["arrow"],
        style="italic",
    )
    ax.text(
        14,
        info_y - 1.25,
        "Full: + conv_history",
        fontsize=info_font - 2,
        ha="center",
        color=COLORS["arrow"],
        style="italic",
    )

    # Assistant agent info
    ax.text(
        24.5,
        info_y + 0.6,
        "System Prompt Inputs:",
        fontsize=info_font + 1,
        ha="center",
        color=COLORS["assistant_light"],
        fontweight="bold",
    )
    ax.text(
        24.5,
        info_y - 0.1,
        "tools + messages[]",
        fontsize=info_font,
        ha="center",
        color=COLORS["text"],
        family="monospace",
    )
    ax.text(
        24.5,
        info_y - 0.7,
        "(includes ask_user tool,",
        fontsize=info_font - 2,
        ha="center",
        color=COLORS["highlight"],
        style="italic",
    )
    ax.text(
        24.5,
        info_y - 1.25,
        "hidden in final output)",
        fontsize=info_font - 2,
        ha="center",
        color=COLORS["highlight"],
        style="italic",
    )

    # Simulator agent info
    ax.text(
        36.5,
        info_y + 0.6,
        "System Prompt Inputs:",
        fontsize=info_font + 1,
        ha="center",
        color=COLORS["simulator_light"],
        fontweight="bold",
    )
    ax.text(
        36.5, info_y - 0.1, "conv_history +", fontsize=info_font, ha="center", color=COLORS["text"], family="monospace"
    )
    ax.text(
        36.5,
        info_y - 0.7,
        "tool_name, tool_desc,",
        fontsize=info_font - 2,
        ha="center",
        color=COLORS["text"],
        family="monospace",
    )
    ax.text(
        36.5, info_y - 1.25, "tool_args", fontsize=info_font - 2, ha="center", color=COLORS["text"], family="monospace"
    )

    # State transitions - labels CLOSE to arrows
    ax.annotate(
        "",
        xy=(11, node_y),
        xytext=(7.2, node_y),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["highlight"], lw=5, mutation_scale=25),
    )
    ax.text(
        9.1, node_y + 0.6, "entry", fontsize=24, color=COLORS["highlight"], fontweight="bold", ha="center", va="bottom"
    )

    ax.annotate(
        "",
        xy=(20, node_y),
        xytext=(17, node_y),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["user_light"], lw=5, mutation_scale=25),
    )
    ax.text(
        18.5,
        node_y + 0.6,
        "request",
        fontsize=24,
        color=COLORS["user_light"],
        fontweight="bold",
        ha="center",
        va="bottom",
    )

    # has tools (arc curves DOWN)
    ax.annotate(
        "",
        xy=(32, node_y + 0.6),
        xytext=(29, node_y + 0.6),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["assistant_light"], lw=5, mutation_scale=25, connectionstyle="arc3,rad=-0.35"
        ),
    )
    ax.text(
        30.5,
        node_y + 2.6,
        "has tools",
        fontsize=24,
        color=COLORS["assistant_light"],
        fontweight="bold",
        ha="center",
        va="bottom",
    )

    # results (arc curves UP)
    ax.annotate(
        "",
        xy=(29, node_y - 0.6),
        xytext=(32, node_y - 0.6),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["simulator_light"], lw=5, mutation_scale=25, connectionstyle="arc3,rad=-0.35"
        ),
    )

    # text only (arc curves UP)
    ax.annotate(
        "",
        xy=(17, node_y - 0.6),
        xytext=(20, node_y - 0.6),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["assistant_light"], lw=5, mutation_scale=25, connectionstyle="arc3,rad=-0.35"
        ),
    )

    # Termination arrow (higher arc from user to END to avoid simulator overlap)
    ax.annotate(
        "",
        xy=(44.8, node_y + 0.3),
        xytext=(14, node_y + 1.1),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["error"], lw=4, connectionstyle="arc3,rad=-0.12", mutation_scale=22
        ),
    )
    ax.text(
        29,
        17.6,
        '"thank you" OR iter >= 15',
        fontsize=22,
        color=COLORS["error"],
        fontweight="bold",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.25", facecolor=COLORS["card_bg"], edgecolor=COLORS["error"], lw=2),
    )

    # === SYSTEM INPUTS (no box, aligned with System Prompt Inputs) ===
    ax.text(
        6,
        info_y + 0.6,
        "System Inputs:",
        fontsize=info_font + 1,
        fontweight="bold",
        color=COLORS["highlight"],
        ha="center",
    )
    ax.text(6, info_y - 0.1, "• ASTRA 1-tool tasks", fontsize=info_font, color=COLORS["text"], ha="center")
    ax.text(6, info_y - 0.7, '• "Correct" match tool', fontsize=info_font - 2, color=COLORS["text"], ha="center")
    ax.text(6, info_y - 1.25, "• MCP tool metadata", fontsize=info_font - 2, color=COLORS["text"], ha="center")

    # === BOTTOM PANELS ===
    panel_y = 0.5
    panel_h = 4.2
    panel_w = 15.0

    # SPECIAL FEATURES (left) - orange color
    draw_rounded_box(ax, 2, panel_y, panel_w, panel_h, COLORS["card_bg"], COLORS["mcp"], lw=3)
    ax.text(
        2 + panel_w / 2,
        panel_y + panel_h - 0.55,
        "SPECIAL FEATURES",
        fontsize=28,
        fontweight="bold",
        ha="center",
        color=COLORS["mcp"],
    )
    features = [
        ("ask_user tool (hidden in output)", COLORS["mcp"]),
        ("→ replies shown as HumanMessage", COLORS["user_light"]),
        ("Full history mode available", COLORS["text"]),
        ("Max 3 retries on failures", COLORS["text"]),
    ]
    for i, (feat, color) in enumerate(features):
        ax.text(2.5, panel_y + panel_h - 1.3 - i * 0.72, f"• {feat}", fontsize=20, color=color)

    # MESSAGE TYPES (center)
    draw_rounded_box(ax, 18.5, panel_y, panel_w, panel_h, COLORS["card_bg"], COLORS["border"], lw=3)
    ax.text(
        18.5 + panel_w / 2,
        panel_y + panel_h - 0.55,
        "MESSAGE TYPES",
        fontsize=28,
        fontweight="bold",
        ha="center",
        color=COLORS["text"],
    )
    msgs = [
        ("HumanMessage = user input", COLORS["user_light"]),
        ("AIMessage = assistant output", COLORS["assistant_light"]),
        ("ToolMessage = tool results", COLORS["simulator_light"]),
        ("SystemMessage = prompts", COLORS["arrow"]),
    ]
    for i, (msg, color) in enumerate(msgs):
        ax.text(19, panel_y + panel_h - 1.3 - i * 0.72, f"• {msg}", fontsize=20, color=color, fontweight="bold")

    # JSON OUTPUTS (right)
    draw_rounded_box(ax, 35, panel_y, panel_w, panel_h, COLORS["card_bg"], COLORS["output"], lw=3)
    ax.text(
        35 + panel_w / 2,
        panel_y + panel_h - 0.55,
        "JSON OUTPUTS",
        fontsize=28,
        fontweight="bold",
        ha="center",
        color=COLORS["output"],
    )
    outputs = [
        ("synthetic_conversations", COLORS["text"]),
        ("number_tools_called", COLORS["text"]),
        ("tools_called_turnidx", COLORS["text"]),
        ("ask_user_turnidx", COLORS["text"]),
    ]
    for i, (out, color) in enumerate(outputs):
        ax.text(35.5, panel_y + panel_h - 1.3 - i * 0.72, f"• {out}", fontsize=20, color=color, family="monospace")

    plt.tight_layout()
    plt.savefig(
        "/Users/melhelou/Desktop/identity-auth-server/evaluation/task_tool_matcher/data/mas_workflow_v1.png",
        dpi=120,
        facecolor=COLORS["bg"],
        edgecolor="none",
        bbox_inches="tight",
    )
    plt.close()
    print("Iteration 1 saved: mas_workflow_v1.png")


def create_iteration_2():
    """Iteration 2: Improved visual hierarchy and added prompts section."""
    fig, ax = plt.subplots(1, 1, figsize=(26, 20))
    ax.set_xlim(0, 26)
    ax.set_ylim(0, 20)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    # Title with gradient-like effect
    ax.text(
        13,
        19.3,
        "Multi-Agent System (MAS)",
        fontsize=32,
        fontweight="bold",
        ha="center",
        va="center",
        color=COLORS["text"],
    )
    ax.text(
        13,
        18.5,
        "Conversation Simulation Architecture",
        fontsize=18,
        ha="center",
        va="center",
        color=COLORS["assistant_light"],
    )
    ax.text(
        13,
        17.9,
        "for Task-Tool Matcher Evaluation",
        fontsize=14,
        ha="center",
        va="center",
        color=COLORS["arrow"],
        style="italic",
    )

    # Decorative lines
    ax.plot([3, 23], [17.5, 17.5], color=COLORS["assistant"], linewidth=3, alpha=0.4)
    ax.plot([4, 22], [17.4, 17.4], color=COLORS["assistant_light"], linewidth=1, alpha=0.3)

    # Main workflow box
    draw_rounded_box(ax, 0.5, 8.5, 25, 8.5, COLORS["card_bg"], COLORS["border"], alpha=0.5, lw=1)
    ax.text(13, 16.7, "AGENT WORKFLOW", fontsize=14, fontweight="bold", ha="center", color=COLORS["text"], alpha=0.7)

    # Agents (larger, more prominent)
    agent_y = 10
    agent_h = 5

    draw_agent(
        ax,
        1,
        agent_y,
        7,
        agent_h,
        COLORS["user"],
        COLORS["user_light"],
        "U",
        "User Agent",
        [
            "Simulates realistic human behavior",
            "Can be vague, omit details initially",
            "Provides missing info when asked",
            "Evaluates if objective is achieved",
            'Says "thank you" when satisfied',
        ],
        "gpt-4o | temp=0.7",
    )

    draw_agent(
        ax,
        9.5,
        agent_y,
        7,
        agent_h,
        COLORS["assistant"],
        COLORS["assistant_light"],
        "A",
        "Assistant Agent",
        [
            "AI assistant with tool access",
            "Processes user requests",
            "Decides when to invoke tools",
            "Uses ask_user for clarification",
            "Bound with MCP server tools",
        ],
        "gpt-4o | temp=0.3 | tools",
    )

    draw_agent(
        ax,
        18,
        agent_y,
        7,
        agent_h,
        COLORS["simulator"],
        COLORS["simulator_light"],
        "T",
        "Tool Simulator",
        [
            "Generates realistic tool outputs",
            "Maintains conversation context",
            "No actual API calls made",
            "Context-aware responses",
            "Consistent with past messages",
        ],
        "gpt-4o | temp=0.5",
    )

    # Workflow arrows (larger labels)
    draw_arrow(ax, (8, 12.5), (9.5, 12.5), COLORS["user_light"], label="HumanMessage", lw=3)
    draw_arrow(ax, (16.5, 13.5), (18, 13.5), COLORS["assistant_light"], curved=0.2, label="tool_calls", lw=3)
    draw_arrow(ax, (18, 11.5), (16.5, 11.5), COLORS["simulator_light"], curved=0.2, label="ToolMessage", lw=3)
    draw_arrow(ax, (9.5, 11.5), (8, 11.5), COLORS["assistant_light"], curved=-0.2, label="AIMessage (text)", lw=3)

    # Input/Output with more detail
    draw_rounded_box(ax, 1, 1, 8, 3, COLORS["card_bg"], COLORS["input"], lw=2)
    ax.text(5, 3.6, "INPUTS", fontsize=14, fontweight="bold", ha="center", color=COLORS["input"])
    inputs = [
        "--tasks-file: synthetic_tasks.json",
        "--mcp-servers-dir: MCP definitions",
        "--output-file: results.json",
        "--use-full-history (optional)",
        "--debug, --verbose, --sample",
    ]
    for i, inp in enumerate(inputs):
        ax.text(1.3, 3.1 - i * 0.4, f"• {inp}", fontsize=9, color=COLORS["text"])

    draw_rounded_box(ax, 17, 1, 8, 3, COLORS["card_bg"], COLORS["output"], lw=2)
    ax.text(21, 3.6, "OUTPUTS", fontsize=14, fontweight="bold", ha="center", color=COLORS["output"])
    outputs = [
        "synthetic_conversations: []",
        "conversation_iters: iteration counts",
        "number_tools_called: unique tools",
        "tools_called_turnidx: turn indices",
        "timing data per MCP server",
    ]
    for i, out in enumerate(outputs):
        ax.text(17.3, 3.1 - i * 0.4, f"• {out}", fontsize=9, color=COLORS["text"])

    # State machine (centered at bottom)
    draw_rounded_box(ax, 9, 1, 8, 3, COLORS["card_bg"], COLORS["highlight"], lw=2, alpha=0.8)
    ax.text(13, 3.6, "STATE MACHINE", fontsize=12, fontweight="bold", ha="center", color=COLORS["highlight"])

    # Mini state diagram
    mini_y = 2
    mini_nodes = [
        (10, mini_y, "S", COLORS["highlight"]),
        (11.5, mini_y, "U", COLORS["user"]),
        (13, mini_y, "A", COLORS["assistant"]),
        (14.5, mini_y, "T", COLORS["simulator"]),
        (16, mini_y, "E", COLORS["error"]),
    ]
    for nx, ny, lbl, col in mini_nodes:
        c = Circle((nx, ny), 0.35, facecolor=col, edgecolor="white", lw=1.5)
        ax.add_patch(c)
        ax.text(nx, ny, lbl, fontsize=10, ha="center", va="center", color="white", fontweight="bold")

    # Mini arrows
    for i in range(len(mini_nodes) - 1):
        ax.annotate(
            "",
            xy=(mini_nodes[i + 1][0] - 0.4, mini_y),
            xytext=(mini_nodes[i][0] + 0.4, mini_y),
            arrowprops=dict(arrowstyle="->", color=COLORS["arrow"], lw=1.5),
        )

    # Info panels
    draw_info_panel(
        ax,
        1,
        4.5,
        6,
        3.5,
        "System Prompts",
        [
            ("USER_AGENT_PROMPT", COLORS["user_light"]),
            ("USER_EVALUATION_PROMPT", COLORS["user_light"]),
            ("ASSISTANT_AGENT_PROMPT", COLORS["assistant_light"]),
            ("SIMULATOR_AGENT_PROMPT", COLORS["simulator_light"]),
            ("ASK_USER_PROMPT (hidden)", COLORS["highlight"]),
        ],
        COLORS["text"],
        COLORS["border"],
    )

    draw_info_panel(
        ax,
        19,
        4.5,
        6,
        3.5,
        "Key Features",
        [
            ("Realistic human simulation", COLORS["user_light"]),
            ("Dynamic tool binding", COLORS["assistant_light"]),
            ("Context-aware simulation", COLORS["simulator_light"]),
            ("ask_user transparency", COLORS["highlight"]),
            ("Max 15 iteration limit", COLORS["error"]),
        ],
        COLORS["text"],
        COLORS["border"],
    )

    plt.tight_layout()
    plt.savefig(
        "/Users/melhelou/Desktop/identity-auth-server/evaluation/task_tool_matcher/data/mas_workflow_v2.png",
        dpi=200,
        facecolor=COLORS["bg"],
        edgecolor="none",
        bbox_inches="tight",
    )
    plt.close()
    print("Iteration 2 saved: mas_workflow_v2.png")


def create_iteration_3():
    """Iteration 3: Added conversation flow example and improved aesthetics."""
    fig, ax = plt.subplots(1, 1, figsize=(28, 22))
    ax.set_xlim(0, 28)
    ax.set_ylim(0, 22)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    # Title
    ax.text(14, 21.3, "Multi-Agent System (MAS)", fontsize=34, fontweight="bold", ha="center", color=COLORS["text"])
    ax.text(
        14,
        20.5,
        "LangGraph Conversation Simulation for Task-Tool Evaluation",
        fontsize=16,
        ha="center",
        color=COLORS["arrow"],
        style="italic",
    )

    # Top gradient bar
    for i, alpha in enumerate([0.5, 0.3, 0.15]):
        ax.plot(
            [2 + i * 0.3, 26 - i * 0.3],
            [20 - i * 0.1, 20 - i * 0.1],
            color=COLORS["assistant"],
            linewidth=4 - i,
            alpha=alpha,
        )

    # Main section: Three agents
    ax.text(14, 19.3, "CORE AGENTS", fontsize=16, fontweight="bold", ha="center", color=COLORS["text"], alpha=0.8)

    agent_y = 13.5
    agent_h = 5.2

    draw_agent(
        ax,
        1,
        agent_y,
        7.5,
        agent_h,
        COLORS["user"],
        COLORS["user_light"],
        "U",
        "User Agent",
        [
            "Simulates realistic human behavior",
            "Omits details like a real human",
            "Provides info when assistant asks",
            "Evaluates objective completion",
            'Terminates with "thank you"',
        ],
        "gpt-4o | temperature=0.7",
    )

    draw_agent(
        ax,
        10.25,
        agent_y,
        7.5,
        agent_h,
        COLORS["assistant"],
        COLORS["assistant_light"],
        "A",
        "Assistant Agent",
        [
            "AI assistant with MCP tools",
            "Processes user requests",
            "Invokes tools when needed",
            "Uses ask_user for missing info",
            "Returns text or tool calls",
        ],
        "gpt-4o | temperature=0.3",
    )

    draw_agent(
        ax,
        19.5,
        agent_y,
        7.5,
        agent_h,
        COLORS["simulator"],
        COLORS["simulator_light"],
        "T",
        "Tool Simulator",
        [
            "Generates realistic tool outputs",
            "Maintains full conversation context",
            "No real API calls made",
            "Synthesizes plausible results",
            "Consistent with conversation",
        ],
        "gpt-4o | temperature=0.5",
    )

    # Arrows between agents
    draw_arrow(ax, (8.5, 16), (10.25, 16), COLORS["user_light"], label="HumanMessage", lw=3)
    draw_arrow(ax, (17.75, 17), (19.5, 17), COLORS["assistant_light"], curved=0.15, label="tool_calls", lw=3)
    draw_arrow(ax, (19.5, 15), (17.75, 15), COLORS["simulator_light"], curved=0.15, label="ToolMessage", lw=3)
    draw_arrow(ax, (10.25, 15), (8.5, 15), COLORS["assistant_light"], curved=-0.15, label="AIMessage", lw=3)

    # Conversation example section
    draw_rounded_box(ax, 1, 6.5, 12, 6.5, COLORS["card_bg"], COLORS["border"], lw=2)
    ax.text(7, 12.5, "EXAMPLE CONVERSATION FLOW", fontsize=13, fontweight="bold", ha="center", color=COLORS["text"])

    conv_items = [
        ("1. User:", '"Book me a flight to Paris"', COLORS["user_light"]),
        ("2. Assistant:", "[calls search_flights tool]", COLORS["assistant_light"]),
        ("3. Simulator:", '{"flights": [...], "prices": [...]}', COLORS["simulator_light"]),
        ("4. Assistant:", '"I found 3 flights. Which date?"', COLORS["assistant_light"]),
        ("5. User:", '"Next Friday please"', COLORS["user_light"]),
        ("6. Assistant:", "[calls book_flight tool]", COLORS["assistant_light"]),
        ("7. Simulator:", '{"confirmation": "ABC123"}', COLORS["simulator_light"]),
        ("8. Assistant:", '"Booked! Confirmation: ABC123"', COLORS["assistant_light"]),
        ("9. User:", '"Thank you!"', COLORS["user_light"]),
        ("   -> END", "(termination detected)", COLORS["error"]),
    ]
    for i, (role, msg, color) in enumerate(conv_items):
        ax.text(1.5, 11.8 - i * 0.52, role, fontsize=9, color=color, fontweight="bold")
        ax.text(3.5, 11.8 - i * 0.52, msg, fontsize=9, color=COLORS["text"], family="monospace")

    # State machine section
    draw_rounded_box(ax, 14, 6.5, 13, 6.5, COLORS["card_bg"], COLORS["highlight"], lw=2, alpha=0.9)
    ax.text(
        20.5, 12.5, "LANGGRAPH STATE MACHINE", fontsize=13, fontweight="bold", ha="center", color=COLORS["highlight"]
    )

    node_y = 9
    draw_state_node(ax, 15.5, node_y, "START", COLORS["highlight"], is_terminal=True)
    draw_state_node(ax, 18, node_y, "user", COLORS["user"])
    draw_state_node(ax, 21, node_y, "assistant", COLORS["assistant"])
    draw_state_node(ax, 24, node_y, "simulator", COLORS["simulator"])
    draw_state_node(ax, 26, node_y, "END", COLORS["error"], is_terminal=True)

    draw_arrow(ax, (16, node_y), (17.1, node_y), COLORS["highlight"], lw=2)
    draw_arrow(ax, (18.9, node_y), (20.1, node_y), COLORS["user_light"], lw=2)
    draw_arrow(ax, (21.9, node_y + 0.3), (23.1, node_y + 0.3), COLORS["assistant_light"], curved=0.1, lw=2)
    draw_arrow(ax, (23.1, node_y - 0.3), (21.9, node_y - 0.3), COLORS["simulator_light"], curved=0.1, lw=2)
    draw_arrow(ax, (20.1, node_y - 0.3), (18.9, node_y - 0.3), COLORS["assistant_light"], curved=-0.15, lw=2)

    ax.annotate(
        "",
        xy=(25.5, node_y),
        xytext=(18.9, node_y + 0.5),
        arrowprops=dict(arrowstyle="->", color=COLORS["error"], lw=2, connectionstyle="arc3,rad=0.1"),
    )

    # Transition labels
    ax.text(17.5, node_y + 0.5, "init", fontsize=8, color=COLORS["highlight"])
    ax.text(19.5, node_y + 0.5, "msg", fontsize=8, color=COLORS["user_light"])
    ax.text(22.5, node_y + 0.8, "tools", fontsize=8, color=COLORS["assistant_light"])
    ax.text(22.5, node_y - 0.8, "result", fontsize=8, color=COLORS["simulator_light"])
    ax.text(19.5, node_y - 0.8, "text", fontsize=8, color=COLORS["assistant_light"])
    ax.text(22, node_y + 1.3, "done", fontsize=8, color=COLORS["error"])

    # AgentState definition
    ax.text(
        20.5,
        7.5,
        "AgentState = {messages, objective, next_agent, iteration_count}",
        fontsize=9,
        ha="center",
        color=COLORS["arrow"],
        family="monospace",
    )

    # Bottom section: I/O and features
    draw_rounded_box(ax, 1, 1, 8, 5, COLORS["card_bg"], COLORS["input"], lw=2)
    ax.text(5, 5.5, "CLI INPUTS", fontsize=12, fontweight="bold", ha="center", color=COLORS["input"])
    inputs = [
        ("--tasks-file", "Synthetic tasks JSON"),
        ("--mcp-servers-dir", "MCP tool definitions"),
        ("--output-file", "Results destination"),
        ("--use-full-history", "Full context mode"),
        ("--debug", "Verbose logging"),
        ("--sample", "Run 5 per MCP server"),
    ]
    for i, (flag, desc) in enumerate(inputs):
        ax.text(1.3, 4.8 - i * 0.6, flag, fontsize=9, color=COLORS["input"], family="monospace", fontweight="bold")
        ax.text(4.5, 4.8 - i * 0.6, desc, fontsize=9, color=COLORS["text"])

    draw_rounded_box(ax, 10, 1, 8, 5, COLORS["card_bg"], COLORS["border"], lw=2)
    ax.text(14, 5.5, "SPECIAL FEATURES", fontsize=12, fontweight="bold", ha="center", color=COLORS["text"])
    features = [
        ("ask_user tool", "Hidden clarification mechanism"),
        ("Full history", "Complete context for evaluation"),
        ("Retry logic", "Max 3 retries on failure"),
        ("Per-MCP output", "Separate JSON per server"),
        ("Timing metrics", "Performance tracking"),
    ]
    for i, (feat, desc) in enumerate(features):
        ax.text(10.3, 4.8 - i * 0.6, feat, fontsize=9, color=COLORS["highlight"], fontweight="bold")
        ax.text(13.5, 4.8 - i * 0.6, desc, fontsize=9, color=COLORS["text"])

    draw_rounded_box(ax, 19, 1, 8, 5, COLORS["card_bg"], COLORS["output"], lw=2)
    ax.text(23, 5.5, "JSON OUTPUTS", fontsize=12, fontweight="bold", ha="center", color=COLORS["output"])
    outputs = [
        ("synthetic_conversations", "Full message list"),
        ("conversation_iters", "Iteration count"),
        ("number_tools_called", "Unique tools used"),
        ("tools_called_turnidx", "Tool call positions"),
        ("ask_user_turnidx", "Clarification points"),
    ]
    for i, (field, desc) in enumerate(outputs):
        ax.text(19.3, 4.8 - i * 0.6, field, fontsize=9, color=COLORS["output"], family="monospace")
        ax.text(23, 4.8 - i * 0.6, desc, fontsize=8, color=COLORS["text"])

    plt.tight_layout()
    plt.savefig(
        "/Users/melhelou/Desktop/identity-auth-server/evaluation/task_tool_matcher/data/mas_workflow_v3.png",
        dpi=200,
        facecolor=COLORS["bg"],
        edgecolor="none",
        bbox_inches="tight",
    )
    plt.close()
    print("Iteration 3 saved: mas_workflow_v3.png")


def create_iteration_4():
    """Iteration 4: Polished design with better visual flow and hierarchy."""
    fig, ax = plt.subplots(1, 1, figsize=(30, 24))
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 24)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    # Header
    ax.text(
        15,
        23.2,
        "MULTI-AGENT SYSTEM (MAS)",
        fontsize=36,
        fontweight="bold",
        ha="center",
        color=COLORS["text"],
        family="sans-serif",
    )
    ax.text(
        15, 22.3, "LangGraph-Powered Conversation Simulation", fontsize=20, ha="center", color=COLORS["assistant_light"]
    )
    ax.text(
        15,
        21.6,
        "for Evaluating Task-Tool Matchers in Zero Trust Authorization",
        fontsize=14,
        ha="center",
        color=COLORS["arrow"],
        style="italic",
    )

    # Decorative header line
    ax.fill_between([2, 28], [21.2, 21.2], [21.1, 21.1], color=COLORS["assistant"], alpha=0.5)
    ax.fill_between([3, 27], [21.05, 21.05], [21.0, 21.0], color=COLORS["assistant_light"], alpha=0.3)

    # === SECTION 1: DATA PIPELINE (Top) ===
    draw_rounded_box(ax, 1, 18, 28, 2.8, COLORS["card_bg"], COLORS["border"], alpha=0.6, lw=1)
    ax.text(15, 20.4, "DATA PIPELINE", fontsize=14, fontweight="bold", ha="center", color=COLORS["text"], alpha=0.8)

    # Pipeline boxes
    pipeline_items = [
        (2.5, "Tasks JSON", COLORS["input"], "synthetic_tasks\n+ objectives"),
        (8, "MCP Servers", COLORS["mcp"], "tool definitions\n+ schemas"),
        (13.5, "MAS Engine", COLORS["assistant"], "LangGraph\nworkflow"),
        (19, "Conversations", COLORS["output"], "serialized\nmessages"),
        (24.5, "Metrics", COLORS["highlight"], "timing +\nstatistics"),
    ]
    for px, label, color, sublabel in pipeline_items:
        draw_rounded_box(ax, px, 18.3, 4, 1.8, color, "white", alpha=0.9, lw=2, radius=0.2)
        ax.text(px + 2, 19.5, label, fontsize=11, ha="center", va="center", color="white", fontweight="bold")
        ax.text(px + 2, 18.8, sublabel, fontsize=8, ha="center", va="center", color="white", alpha=0.8)

    # Pipeline arrows
    for i in range(len(pipeline_items) - 1):
        ax.annotate(
            "",
            xy=(pipeline_items[i + 1][0], 19.2),
            xytext=(pipeline_items[i][0] + 4.2, 19.2),
            arrowprops=dict(arrowstyle="->", color=COLORS["arrow"], lw=2.5),
        )

    # === SECTION 2: AGENT ARCHITECTURE (Middle) ===
    ax.text(
        15, 17.3, "AGENT ARCHITECTURE", fontsize=14, fontweight="bold", ha="center", color=COLORS["text"], alpha=0.8
    )

    agent_y = 11
    agent_h = 5.8
    agent_w = 8

    # User Agent
    draw_agent(
        ax,
        1.5,
        agent_y,
        agent_w,
        agent_h,
        COLORS["user"],
        COLORS["user_light"],
        "U",
        "User Agent",
        [
            "Simulates realistic human behavior",
            "May omit details initially (realistic)",
            "Provides missing info when asked",
            "Evaluates if objective is achieved",
            'Says "thank you" when satisfied',
            "-> Triggers conversation END",
        ],
        "ChatOpenAI | gpt-4o | temp=0.7",
    )

    # Assistant Agent
    draw_agent(
        ax,
        11,
        agent_y,
        agent_w,
        agent_h,
        COLORS["assistant"],
        COLORS["assistant_light"],
        "A",
        "Assistant Agent",
        [
            "Main AI with tool-calling capability",
            "Processes requests from User Agent",
            "Bound with MCP server tools",
            "Invokes tools via tool_calls",
            "Uses ask_user for clarification",
            "Returns AIMessage (text or tools)",
        ],
        "ChatOpenAI | gpt-4o | temp=0.3 | tools",
    )

    # Tool Simulator
    draw_agent(
        ax,
        20.5,
        agent_y,
        agent_w,
        agent_h,
        COLORS["simulator"],
        COLORS["simulator_light"],
        "T",
        "Tool Simulator",
        [
            "Generates realistic tool outputs",
            "Full conversation context aware",
            "No actual API calls made",
            "Synthesizes plausible results",
            "Maintains consistency",
            "Returns ToolMessage",
        ],
        "ChatOpenAI | gpt-4o | temp=0.5",
    )

    # Main workflow arrows
    arrow_y_top = 14.5
    arrow_y_bot = 12.5

    draw_arrow(ax, (9.5, arrow_y_top), (11, arrow_y_top), COLORS["user_light"], label="HumanMessage", lw=3.5)
    draw_arrow(
        ax,
        (19, arrow_y_top + 0.5),
        (20.5, arrow_y_top + 0.5),
        COLORS["assistant_light"],
        curved=0.1,
        label="tool_calls",
        lw=3.5,
    )
    draw_arrow(
        ax,
        (20.5, arrow_y_bot - 0.5),
        (19, arrow_y_bot - 0.5),
        COLORS["simulator_light"],
        curved=0.1,
        label="ToolMessage",
        lw=3.5,
    )
    draw_arrow(
        ax, (11, arrow_y_bot), (9.5, arrow_y_bot), COLORS["assistant_light"], curved=-0.1, label="AIMessage", lw=3.5
    )

    # ask_user special flow
    ax.annotate(
        "",
        xy=(5.5, 11.5),
        xytext=(11, 12.5),
        arrowprops=dict(
            arrowstyle="->", color=COLORS["highlight"], lw=2, connectionstyle="arc3,rad=-0.3", linestyle="--"
        ),
    )
    ax.text(8, 11.2, "ask_user", fontsize=9, color=COLORS["highlight"], rotation=-20, fontweight="bold")

    # === SECTION 3: STATE MACHINE (Lower middle) ===
    draw_rounded_box(ax, 1, 4.5, 28, 6, COLORS["card_bg"], COLORS["highlight"], alpha=0.8, lw=2)
    ax.text(15, 10, "LANGGRAPH STATE MACHINE", fontsize=15, fontweight="bold", ha="center", color=COLORS["highlight"])

    # State nodes (larger, clearer)
    node_y = 7
    nodes = [
        (4, "START", COLORS["highlight"], True),
        (8.5, "user", COLORS["user"], False),
        (15, "assistant", COLORS["assistant"], False),
        (21.5, "simulator", COLORS["simulator"], False),
        (26, "END", COLORS["error"], True),
    ]

    for nx, label, color, is_terminal in nodes:
        draw_state_node(ax, nx, node_y, label, color, is_terminal)

    # State transitions
    draw_arrow(ax, (4.5, node_y), (7.6, node_y), COLORS["highlight"], lw=2.5)
    draw_arrow(ax, (9.4, node_y), (14.1, node_y), COLORS["user_light"], lw=2.5)
    draw_arrow(ax, (15.9, node_y + 0.4), (20.6, node_y + 0.4), COLORS["assistant_light"], curved=0.1, lw=2.5)
    draw_arrow(ax, (20.6, node_y - 0.4), (15.9, node_y - 0.4), COLORS["simulator_light"], curved=0.1, lw=2.5)
    draw_arrow(ax, (14.1, node_y - 0.4), (9.4, node_y - 0.4), COLORS["assistant_light"], curved=-0.15, lw=2.5)

    # Termination arrow
    ax.annotate(
        "",
        xy=(25.5, node_y),
        xytext=(9.4, node_y + 0.6),
        arrowprops=dict(arrowstyle="->", color=COLORS["error"], lw=2.5, connectionstyle="arc3,rad=0.08"),
    )

    # Transition labels
    ax.text(6.2, node_y + 0.5, "init", fontsize=10, color=COLORS["highlight"], fontweight="bold")
    ax.text(11.7, node_y + 0.5, "request", fontsize=10, color=COLORS["user_light"], fontweight="bold")
    ax.text(18.2, node_y + 1.1, "has tool_calls", fontsize=9, color=COLORS["assistant_light"])
    ax.text(18.2, node_y - 1.1, "tool results", fontsize=9, color=COLORS["simulator_light"])
    ax.text(11.7, node_y - 1.1, "text response", fontsize=9, color=COLORS["assistant_light"])
    ax.text(17, node_y + 1.8, '"thank you" OR iterations >= 15', fontsize=10, color=COLORS["error"], fontweight="bold")

    # AgentState type definition
    draw_rounded_box(ax, 2, 4.8, 10, 1.2, COLORS["card_bg"], COLORS["border"], alpha=0.9)
    ax.text(7, 5.7, "AgentState TypedDict", fontsize=10, fontweight="bold", ha="center", color=COLORS["text"])
    ax.text(
        7,
        5.2,
        "messages | objective | next_agent | iteration_count",
        fontsize=8,
        ha="center",
        color=COLORS["arrow"],
        family="monospace",
    )

    # === SECTION 4: INFO PANELS (Bottom) ===
    # Inputs
    draw_rounded_box(ax, 1, 0.5, 7, 3.5, COLORS["card_bg"], COLORS["input"], lw=2)
    ax.text(4.5, 3.6, "CLI ARGUMENTS", fontsize=11, fontweight="bold", ha="center", color=COLORS["input"])
    cli_args = [
        "--tasks-file (required)",
        "--mcp-servers-dir (required)",
        "--output-file (required)",
        "--use-full-history",
        "--debug | --verbose | --sample",
    ]
    for i, arg in enumerate(cli_args):
        ax.text(1.3, 3.0 - i * 0.5, arg, fontsize=9, color=COLORS["text"], family="monospace")

    # Features
    draw_rounded_box(ax, 8.5, 0.5, 6, 3.5, COLORS["card_bg"], COLORS["highlight"], lw=2)
    ax.text(11.5, 3.6, "KEY FEATURES", fontsize=11, fontweight="bold", ha="center", color=COLORS["highlight"])
    features = [
        "Realistic human simulation",
        "Hidden ask_user mechanism",
        "Full context evaluation",
        "3x retry on failure",
        "Per-MCP server outputs",
    ]
    for i, feat in enumerate(features):
        ax.text(8.8, 3.0 - i * 0.5, f"• {feat}", fontsize=9, color=COLORS["text"])

    # Outputs
    draw_rounded_box(ax, 15, 0.5, 6.5, 3.5, COLORS["card_bg"], COLORS["output"], lw=2)
    ax.text(18.25, 3.6, "OUTPUT FIELDS", fontsize=11, fontweight="bold", ha="center", color=COLORS["output"])
    outputs = [
        "synthetic_conversations",
        "conversation_iters",
        "number_tools_called",
        "tools_called_turnidx",
        "ask_user_turnidx",
    ]
    for i, out in enumerate(outputs):
        ax.text(15.3, 3.0 - i * 0.5, out, fontsize=9, color=COLORS["text"], family="monospace")

    # Termination
    draw_rounded_box(ax, 22, 0.5, 7, 3.5, COLORS["card_bg"], COLORS["error"], lw=2)
    ax.text(25.5, 3.6, "TERMINATION", fontsize=11, fontweight="bold", ha="center", color=COLORS["error"])
    term = ['User says "thank you"', 'User says "thanks"', "iteration_count >= 15", "", "Detected in _user_agent()"]
    for i, t in enumerate(term):
        color = COLORS["success"] if i < 2 else COLORS["error"] if i == 2 else COLORS["arrow"]
        ax.text(22.3, 3.0 - i * 0.5, t, fontsize=9, color=color)

    plt.tight_layout()
    plt.savefig(
        "/Users/melhelou/Desktop/identity-auth-server/evaluation/task_tool_matcher/data/mas_workflow_v4.png",
        dpi=200,
        facecolor=COLORS["bg"],
        edgecolor="none",
        bbox_inches="tight",
    )
    plt.close()
    print("Iteration 4 saved: mas_workflow_v4.png")


def create_iteration_5():
    """Iteration 5: Final polished version with all improvements."""
    fig, ax = plt.subplots(1, 1, figsize=(32, 26))
    ax.set_xlim(0, 32)
    ax.set_ylim(0, 26)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    # === HEADER ===
    ax.text(16, 25.2, "MULTI-AGENT SYSTEM (MAS)", fontsize=72, fontweight="bold", ha="center", color=COLORS["text"])
    ax.text(
        16,
        23.5,
        "LangGraph-Powered Conversation Simulation Engine",
        fontsize=40,
        ha="center",
        color=COLORS["assistant_light"],
    )
    ax.text(
        16,
        22.2,
        "Generating Synthetic Conversations for Task-Tool Matcher Evaluation",
        fontsize=30,
        ha="center",
        color=COLORS["arrow"],
        style="italic",
    )

    # Header decorative line
    ax.fill_between([2, 30], [21.5, 21.5], [21.35, 21.35], color=COLORS["assistant_light"], alpha=0.6)

    # === SECTION 1: PIPELINE OVERVIEW ===
    ax.text(16, 20.5, "DATA PIPELINE", fontsize=36, fontweight="bold", ha="center", color=COLORS["text"])

    pipeline_y = 18.5
    pipeline = [
        (3.2, "INPUT", "Tasks JSON\n+ MCP Servers", COLORS["input"]),
        (9.6, "LOAD", "filter_and_convert\n_tools()", COLORS["mcp"]),
        (16, "EXECUTE", "MultiAgentSystem\n.run(objective)", COLORS["assistant_light"]),
        (22.4, "SERIALIZE", "convert_messages\n_to_serializable()", COLORS["simulator_light"]),
        (28.8, "OUTPUT", "JSON Results\n+ Metrics", COLORS["output"]),
    ]

    for px, title, desc, color in pipeline:
        draw_rounded_box(ax, px - 2.4, pipeline_y - 1.2, 4.8, 2.4, COLORS["bg"], color, alpha=0.98, lw=4, radius=0.3)
        ax.text(px, pipeline_y + 0.5, title, fontsize=28, ha="center", va="center", color=color, fontweight="bold")
        ax.text(
            px, pipeline_y - 0.45, desc, fontsize=18, ha="center", va="center", color=COLORS["text"], family="monospace"
        )

    for i in range(len(pipeline) - 1):
        ax.annotate(
            "",
            xy=(pipeline[i + 1][0] - 2.7, pipeline_y),
            xytext=(pipeline[i][0] + 2.7, pipeline_y),
            arrowprops=dict(arrowstyle="-|>", color=COLORS["arrow"], lw=6, mutation_scale=30),
        )

    # === SECTION 2: CORE AGENTS ===
    draw_rounded_box(ax, 1, 8, 30, 8.5, COLORS["card_bg"], COLORS["border"], alpha=0.4, lw=2)
    ax.text(16, 16, "CORE AGENTS", fontsize=36, fontweight="bold", ha="center", color=COLORS["text"])

    # Agent dimensions
    agent_y = 8.5
    agent_h = 6.5
    agent_w = 8.5

    # User Agent
    user_x = 2
    draw_rounded_box(ax, user_x, agent_y, agent_w, agent_h, COLORS["user"], COLORS["user_light"], alpha=0.95, lw=4)
    ax.add_patch(plt.Circle((user_x + 0.8, agent_y + agent_h - 0.8), 0.5, color=COLORS["user_light"], zorder=10))
    ax.text(
        user_x + 0.8,
        agent_y + agent_h - 0.8,
        "U",
        fontsize=28,
        ha="center",
        va="center",
        color=COLORS["user"],
        fontweight="bold",
        zorder=11,
    )
    ax.text(
        user_x + 2.2,
        agent_y + agent_h - 0.8,
        "User Agent",
        fontsize=32,
        fontweight="bold",
        va="center",
        color=COLORS["user_light"],
    )

    user_desc = [
        "Simulates human behavior",
        "May omit details initially",
        "Evaluates completion",
        'Says "thank you" → END',
    ]
    for i, line in enumerate(user_desc):
        ax.text(user_x + 0.4, agent_y + agent_h - 2 - i * 0.75, line, fontsize=20, color=COLORS["text"])
    ax.text(user_x + 0.4, agent_y + 0.4, "gpt-4o | temp=0.7", fontsize=18, color=COLORS["user_light"], style="italic")

    # Assistant Agent
    asst_x = 11.75
    draw_rounded_box(
        ax, asst_x, agent_y, agent_w, agent_h, COLORS["assistant"], COLORS["assistant_light"], alpha=0.95, lw=4
    )
    ax.add_patch(plt.Circle((asst_x + 0.8, agent_y + agent_h - 0.8), 0.5, color=COLORS["assistant_light"], zorder=10))
    ax.text(
        asst_x + 0.8,
        agent_y + agent_h - 0.8,
        "A",
        fontsize=28,
        ha="center",
        va="center",
        color=COLORS["assistant"],
        fontweight="bold",
        zorder=11,
    )
    ax.text(
        asst_x + 2.2,
        agent_y + agent_h - 0.8,
        "Assistant Agent",
        fontsize=32,
        fontweight="bold",
        va="center",
        color=COLORS["assistant_light"],
    )

    asst_desc = ["Main AI with tools", "Processes user requests", "Invokes tool_calls[]", "Uses ask_user tool"]
    for i, line in enumerate(asst_desc):
        ax.text(asst_x + 0.4, agent_y + agent_h - 2 - i * 0.75, line, fontsize=20, color=COLORS["text"])
    ax.text(
        asst_x + 0.4,
        agent_y + 0.4,
        "gpt-4o | temp=0.3 | tools",
        fontsize=18,
        color=COLORS["assistant_light"],
        style="italic",
    )

    # Tool Simulator
    tool_x = 21.5
    draw_rounded_box(
        ax, tool_x, agent_y, agent_w, agent_h, COLORS["simulator"], COLORS["simulator_light"], alpha=0.95, lw=4
    )
    ax.add_patch(plt.Circle((tool_x + 0.8, agent_y + agent_h - 0.8), 0.5, color=COLORS["simulator_light"], zorder=10))
    ax.text(
        tool_x + 0.8,
        agent_y + agent_h - 0.8,
        "T",
        fontsize=28,
        ha="center",
        va="center",
        color=COLORS["simulator"],
        fontweight="bold",
        zorder=11,
    )
    ax.text(
        tool_x + 2.2,
        agent_y + agent_h - 0.8,
        "Tool Simulator",
        fontsize=32,
        fontweight="bold",
        va="center",
        color=COLORS["simulator_light"],
    )

    tool_desc = ["Generates tool outputs", "Full context aware", "No actual API calls", "Returns ToolMessage"]
    for i, line in enumerate(tool_desc):
        ax.text(tool_x + 0.4, agent_y + agent_h - 2 - i * 0.75, line, fontsize=20, color=COLORS["text"])
    ax.text(
        tool_x + 0.4, agent_y + 0.4, "gpt-4o | temp=0.5", fontsize=18, color=COLORS["simulator_light"], style="italic"
    )

    # === AGENT ARROWS ===
    arrow_y_top = 13.5
    arrow_y_bot = 10.5

    # User → Assistant: HumanMessage
    ax.annotate(
        "",
        xy=(asst_x, arrow_y_top),
        xytext=(user_x + agent_w, arrow_y_top),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["user_light"], lw=6, mutation_scale=35),
    )
    ax.text(
        (user_x + agent_w + asst_x) / 2,
        arrow_y_top + 0.6,
        "HumanMessage",
        fontsize=24,
        ha="center",
        color=COLORS["user_light"],
        fontweight="bold",
    )

    # Assistant → Tool: tool_calls
    ax.annotate(
        "",
        xy=(tool_x, arrow_y_top + 0.3),
        xytext=(asst_x + agent_w, arrow_y_top + 0.3),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["assistant_light"], lw=6, mutation_scale=35),
    )
    ax.text(
        (asst_x + agent_w + tool_x) / 2,
        arrow_y_top + 1.1,
        "tool_calls",
        fontsize=24,
        ha="center",
        color=COLORS["assistant_light"],
        fontweight="bold",
    )

    # Tool → Assistant: ToolMessage
    ax.annotate(
        "",
        xy=(asst_x + agent_w, arrow_y_bot - 0.3),
        xytext=(tool_x, arrow_y_bot - 0.3),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["simulator_light"], lw=6, mutation_scale=35),
    )
    ax.text(
        (asst_x + agent_w + tool_x) / 2,
        arrow_y_bot - 1.1,
        "ToolMessage",
        fontsize=24,
        ha="center",
        color=COLORS["simulator_light"],
        fontweight="bold",
    )

    # Assistant → User: AIMessage
    ax.annotate(
        "",
        xy=(user_x + agent_w, arrow_y_bot),
        xytext=(asst_x, arrow_y_bot),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["assistant_light"], lw=6, mutation_scale=35),
    )
    ax.text(
        (user_x + agent_w + asst_x) / 2,
        arrow_y_bot - 0.8,
        "AIMessage",
        fontsize=24,
        ha="center",
        color=COLORS["assistant_light"],
        fontweight="bold",
    )

    # ask_user dashed arrow
    ax.annotate(
        "",
        xy=(user_x + agent_w / 2, agent_y + 1.5),
        xytext=(asst_x + 1.5, agent_y + 2.5),
        arrowprops=dict(
            arrowstyle="-|>",
            color=COLORS["highlight"],
            lw=5,
            connectionstyle="arc3,rad=0.3",
            linestyle="--",
            mutation_scale=30,
        ),
    )
    ax.text(
        user_x + agent_w + 0.3,
        agent_y + 1.2,
        "ask_user",
        fontsize=22,
        color=COLORS["highlight"],
        fontweight="bold",
        style="italic",
    )

    # === SECTION 3: STATE MACHINE ===
    draw_rounded_box(ax, 1, 1.8, 30, 5.8, COLORS["card_bg"], COLORS["highlight"], alpha=0.85, lw=4)
    ax.text(16, 7.1, "LANGGRAPH STATE MACHINE", fontsize=36, fontweight="bold", ha="center", color=COLORS["highlight"])

    # State nodes
    node_y = 4.8
    node_r = 0.7
    nodes = [
        (4, "START", COLORS["highlight"]),
        (10, "user", COLORS["user"]),
        (16, "assistant", COLORS["assistant"]),
        (22, "simulator", COLORS["simulator"]),
        (28, "END", COLORS["error"]),
    ]

    for nx, label, color in nodes:
        ax.add_patch(plt.Circle((nx, node_y), node_r, color=color, zorder=10))
        ax.text(nx, node_y, label, fontsize=20, ha="center", va="center", color="white", fontweight="bold", zorder=11)

    # Transitions
    ax.annotate(
        "",
        xy=(10 - node_r - 0.1, node_y),
        xytext=(4 + node_r + 0.1, node_y),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["highlight"], lw=5, mutation_scale=25),
    )
    ax.text(7, node_y + 0.9, "entry_point", fontsize=20, color=COLORS["highlight"], fontweight="bold", ha="center")

    ax.annotate(
        "",
        xy=(16 - node_r - 0.1, node_y),
        xytext=(10 + node_r + 0.1, node_y),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["user_light"], lw=5, mutation_scale=25),
    )
    ax.text(13, node_y + 0.9, "user_request", fontsize=20, color=COLORS["user_light"], fontweight="bold", ha="center")

    ax.annotate(
        "",
        xy=(22 - node_r - 0.1, node_y + 0.3),
        xytext=(16 + node_r + 0.1, node_y + 0.3),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["assistant_light"], lw=5, mutation_scale=25, connectionstyle="arc3,rad=0.2"
        ),
    )
    ax.text(
        19, node_y + 1.5, "tool_calls", fontsize=20, color=COLORS["assistant_light"], fontweight="bold", ha="center"
    )

    ax.annotate(
        "",
        xy=(16 + node_r + 0.1, node_y - 0.3),
        xytext=(22 - node_r - 0.1, node_y - 0.3),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["simulator_light"], lw=5, mutation_scale=25, connectionstyle="arc3,rad=0.2"
        ),
    )
    ax.text(
        19, node_y - 1.3, "tool_results", fontsize=20, color=COLORS["simulator_light"], fontweight="bold", ha="center"
    )

    ax.annotate(
        "",
        xy=(10 + node_r + 0.1, node_y - 0.3),
        xytext=(16 - node_r - 0.1, node_y - 0.3),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["assistant_light"], lw=5, mutation_scale=25, connectionstyle="arc3,rad=0.25"
        ),
    )
    ax.text(
        13, node_y - 1.3, "text_response", fontsize=20, color=COLORS["assistant_light"], fontweight="bold", ha="center"
    )

    # Termination arrow
    ax.annotate(
        "",
        xy=(28 - node_r - 0.1, node_y),
        xytext=(10 + node_r, node_y + 0.6),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["error"], lw=5, connectionstyle="arc3,rad=-0.12", mutation_scale=25
        ),
    )
    ax.text(
        19,
        node_y + 2.1,
        '"thank you" OR iteration >= 15',
        fontsize=22,
        color=COLORS["error"],
        fontweight="bold",
        ha="center",
    )

    # AgentState box
    draw_rounded_box(ax, 2, 2.1, 7, 1.6, COLORS["bg"], COLORS["border"], alpha=0.98, lw=3)
    ax.text(5.5, 3.3, "AgentState", fontsize=22, fontweight="bold", ha="center", color=COLORS["text"])
    ax.text(
        5.5, 2.55, "messages | objective | next", fontsize=16, ha="center", color=COLORS["arrow"], family="monospace"
    )

    # Conditional edges box
    draw_rounded_box(ax, 23, 2.1, 7, 1.6, COLORS["bg"], COLORS["border"], alpha=0.98, lw=3)
    ax.text(26.5, 3.3, "Conditional Edges", fontsize=22, fontweight="bold", ha="center", color=COLORS["text"])
    ax.text(26.5, 2.55, "add_conditional_edges()", fontsize=16, ha="center", color=COLORS["arrow"], family="monospace")

    plt.tight_layout()
    plt.savefig(
        "/Users/melhelou/Desktop/identity-auth-server/evaluation/task_tool_matcher/data/mas_workflow_v5.png",
        dpi=150,
        facecolor=COLORS["bg"],
        edgecolor="none",
        bbox_inches="tight",
    )
    plt.close()
    print("Iteration 5 saved: mas_workflow_v5.png (FINAL)")


if __name__ == "__main__":
    print("Creating MAS workflow diagrams - 5 iterations...")
    print("-" * 50)
    create_iteration_1()
    create_iteration_2()
    create_iteration_3()
    create_iteration_4()
    create_iteration_5()
    print("-" * 50)
    print("All 5 iterations complete!")
    print("Final version: mas_workflow_v5.png")
