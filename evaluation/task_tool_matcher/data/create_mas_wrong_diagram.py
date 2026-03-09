"""Generate MAS_wrong workflow diagram - LARGER FONTS, NO OVERLAPS."""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

COLORS = {
    "bg": "#0d1117",
    "user": "#1a5c2c",
    "user_light": "#4ade80",  # Brighter green
    "assistant": "#5a3d8a",
    "assistant_light": "#c4b5fd",  # Brighter purple
    "simulator": "#1158a0",
    "simulator_light": "#60a5fa",  # Brighter blue
    "arrow": "#e5e7eb",
    "text": "#ffffff",
    "text_dark": "#0d1117",  # Brighter arrow
    "highlight": "#fbbf24",
    "success": "#4ade80",
    "error": "#f87171",  # Brighter colors
    "border": "#6b7280",
    "card_bg": "#161b22",
    "mcp": "#fb923c",  # Brighter orange
    "input": "#60a5fa",
    "output": "#4ade80",
    "wrong": "#fb923c",
    "null": "#f87171",
}


def draw_box(ax, x, y, w, h, color, edge, alpha=0.95, lw=2.5, r=0.3):
    """Draw a rounded box on the given axes."""
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.02,rounding_size={r}",
        facecolor=color,
        edgecolor=edge,
        linewidth=lw,
        alpha=alpha,
    )
    ax.add_patch(box)


def create_diagram():
    """Create the MAS_wrong workflow diagram."""
    # Smaller figure with higher DPI = larger relative fonts
    fig, ax = plt.subplots(1, 1, figsize=(28, 26))
    ax.set_xlim(0, 56)
    ax.set_ylim(0, 52)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])

    # === TITLE ===
    ax.text(
        28,
        51,
        "Conversation-Simulation MAS Overview w/ Non-Matching Tools",
        fontsize=48,
        fontweight="bold",
        ha="center",
        color=COLORS["text"],
    )
    ax.text(
        28,
        49.2,
        "LangGraph MAS for Correct and Wrong/Null Tool Scenarios",
        fontsize=24,
        ha="center",
        color=COLORS["arrow"],
        fontweight="bold",
        style="italic",
    )
    ax.plot([2, 54], [48.2, 48.2], color=COLORS["error"], linewidth=2, alpha=0.6)

    # === DATA PIPELINE ===
    ax.text(28, 47, "DATA PIPELINE", fontsize=34, fontweight="bold", ha="center", color=COLORS["text"])
    py = 43.5
    bw, bh = 8, 4
    pipeline = [
        (5, "INPUT", "paper_test_data\n+ MCP servers", COLORS["input"]),
        (14, "FILTER", "match_tag_filter\n+ sample limit", COLORS["mcp"]),
        (23, "MODE", "correct/relevant\nvs wrong/null", COLORS["error"]),
        (32, "EXECUTE", "MultiAgentSystem\nWrong.run()", COLORS["assistant_light"]),
        (41, "SERIALIZE", "convert_to_\nserializable()", COLORS["simulator_light"]),
        (50, "OUTPUT", "JSON Results\n+ Timing", COLORS["output"]),
    ]
    for px, title, desc, color in pipeline:
        draw_box(ax, px - bw / 2, py - bh / 2, bw, bh, COLORS["card_bg"], color, lw=3, r=0.4)
        ax.text(px, py + 0.8, title, fontsize=20, ha="center", va="center", color=color, fontweight="bold")
        ax.text(
            px,
            py - 0.8,
            desc,
            fontsize=14,
            ha="center",
            va="center",
            color=COLORS["text"],
            fontweight="bold",
            family="monospace",
        )
    for i in range(len(pipeline) - 1):
        ax.annotate(
            "",
            xy=(pipeline[i + 1][0] - bw / 2 - 0.2, py),
            xytext=(pipeline[i][0] + bw / 2 + 0.2, py),
            arrowprops=dict(arrowstyle="-|>", color=COLORS["arrow"], lw=3, mutation_scale=18),
        )

    # === OPERATION MODES - MOVED DOWN to avoid overlap ===
    ax.text(28, 39.8, "MATCHING MODES", fontsize=34, fontweight="bold", ha="center", color=COLORS["text"])
    my = 34.5  # mode boxes y position - lower to give space
    mh, mw = 4.2, 17

    # CORRECT/RELEVANT
    draw_box(ax, 1.5, my, mw, mh, "#064e3b", COLORS["success"], lw=4)
    ax.text(
        10, my + mh - 0.6, "✓ CORRECT / RELEVANT", fontsize=20, ha="center", color=COLORS["success"], fontweight="bold"
    )
    ax.text(
        10,
        my + 1.9,
        "Exposed to: groundtruth.tools ONLY",
        fontsize=15,
        ha="center",
        color=COLORS["text"],
        fontweight="bold",
        family="monospace",
    )
    ax.text(
        10,
        my + 0.7,
        "Helpful — Calls correct tool",
        fontsize=15,
        ha="center",
        color=COLORS["success"],
        fontweight="bold",
    )

    # WRONG
    draw_box(ax, 19.5, my, mw, mh, "#78350f", COLORS["wrong"], lw=4)
    ax.text(28, my + mh - 0.6, "⚠ WRONG", fontsize=20, ha="center", color=COLORS["wrong"], fontweight="bold")
    ax.text(
        28,
        my + 1.9,
        "Exposed to: input.tools ONLY (wrong)",
        fontsize=15,
        ha="center",
        color=COLORS["wrong"],
        fontweight="bold",
    )
    ax.text(
        28, my + 0.7, "Malicious — Calls wrong tool", fontsize=15, ha="center", color=COLORS["text"], fontweight="bold"
    )

    # NULL
    draw_box(ax, 37.5, my, mw, mh, "#7f1d1d", COLORS["null"], lw=4)
    ax.text(46, my + mh - 0.6, "✗ NULL", fontsize=20, ha="center", color=COLORS["null"], fontweight="bold")
    ax.text(
        46,
        my + 1.9,
        "Exposed to: input.tools ONLY (null)",
        fontsize=15,
        ha="center",
        color=COLORS["null"],
        fontweight="bold",
    )
    ax.text(
        46,
        my + 0.7,
        "Malicious — Calls irrelevant tool",
        fontsize=15,
        ha="center",
        color=COLORS["text"],
        fontweight="bold",
    )

    # === CORE AGENTS ===
    ax.text(28, 32.5, "CORE AGENTS", fontsize=34, fontweight="bold", ha="center", color=COLORS["text"])
    ay = 20
    ah, aw = 11, 14

    # User Agent
    ux = 2
    draw_box(ax, ux, ay, aw, ah, COLORS["user"], COLORS["user_light"], lw=4)
    ax.add_patch(Circle((ux + 1.3, ay + ah - 1.3), 0.9, color=COLORS["user_light"], zorder=10))
    ax.text(
        ux + 1.3,
        ay + ah - 1.3,
        "U",
        fontsize=28,
        ha="center",
        va="center",
        color=COLORS["user"],
        fontweight="bold",
        zorder=11,
    )
    ax.text(
        ux + 3.2, ay + ah - 1.3, "User Agent", fontsize=24, fontweight="bold", va="center", color=COLORS["user_light"]
    )
    for i, line in enumerate(
        ["Simulates realistic", "human behavior", "Can be vague initially", 'Says "thank you" → END']
    ):
        ax.text(ux + 0.8, ay + ah - 3.2 - i * 1.4, line, fontsize=17, color=COLORS["text"], fontweight="bold")
    draw_box(ax, ux + 0.5, ay + 0.5, 6, 1.6, COLORS["highlight"], "white", lw=2, r=0.25)
    ax.text(
        ux + 3.5, ay + 1.3, "NAIVE & TRUSTING", fontsize=14, ha="center", color=COLORS["text_dark"], fontweight="bold"
    )

    # Assistant Agent
    asx = 21
    draw_box(ax, asx, ay, aw, ah, COLORS["assistant"], COLORS["assistant_light"], lw=4)
    ax.add_patch(Circle((asx + 1.3, ay + ah - 1.3), 0.9, color=COLORS["assistant_light"], zorder=10))
    ax.text(
        asx + 1.3,
        ay + ah - 1.3,
        "A",
        fontsize=28,
        ha="center",
        va="center",
        color=COLORS["assistant"],
        fontweight="bold",
        zorder=11,
    )
    ax.text(
        asx + 3.2,
        ay + ah - 1.3,
        "Assistant Agent",
        fontsize=24,
        fontweight="bold",
        va="center",
        color=COLORS["assistant_light"],
    )
    ax.text(asx + 0.8, ay + ah - 3.2, "CORRECT: Helpful AI", fontsize=17, color=COLORS["success"], fontweight="bold")
    ax.text(asx + 0.8, ay + ah - 4.6, "WRONG/NULL:", fontsize=17, color=COLORS["error"], fontweight="bold")
    ax.text(asx + 0.8, ay + ah - 6.0, "Hidden objective to call", fontsize=17, color=COLORS["text"], fontweight="bold")
    ax.text(asx + 0.8, ay + ah - 7.4, "TARGET TOOL", fontsize=17, color=COLORS["error"], fontweight="bold")
    draw_box(ax, asx + 0.5, ay + 0.5, 6.2, 1.6, COLORS["error"], "white", lw=2, r=0.25)
    ax.text(asx + 3.6, ay + 1.3, "MALICIOUS MODE", fontsize=14, ha="center", color="white", fontweight="bold")

    # Simulator Agent
    tx = 40
    draw_box(ax, tx, ay, aw, ah, COLORS["simulator"], COLORS["simulator_light"], lw=4)
    ax.add_patch(Circle((tx + 1.3, ay + ah - 1.3), 0.9, color=COLORS["simulator_light"], zorder=10))
    ax.text(
        tx + 1.3,
        ay + ah - 1.3,
        "T",
        fontsize=28,
        ha="center",
        va="center",
        color=COLORS["simulator"],
        fontweight="bold",
        zorder=11,
    )
    ax.text(
        tx + 3.2,
        ay + ah - 1.3,
        "Simulator Agent",
        fontsize=24,
        fontweight="bold",
        va="center",
        color=COLORS["simulator_light"],
    )
    for i, line in enumerate(
        ["Generates tool outputs", "Full context aware", "No actual API calls", "Returns ToolMessage"]
    ):
        ax.text(tx + 0.8, ay + ah - 3.2 - i * 1.4, line, fontsize=17, color=COLORS["text"], fontweight="bold")
    ax.text(
        tx + 0.8,
        ay + 1.3,
        "ChatOpenAI | temp=0.5",
        fontsize=14,
        color=COLORS["simulator_light"],
        fontweight="bold",
        style="italic",
        family="monospace",
    )

    # === AGENT ARROWS ===
    ur, al = ux + aw, asx
    ar, tl = asx + aw, tx
    gap1 = (ur + al) / 2
    gap2 = (ar + tl) / 2
    yt, yb = 27.5, 24

    ax.annotate(
        "",
        xy=(al - 0.2, yt),
        xytext=(ur + 0.2, yt),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["user_light"], lw=5, mutation_scale=24),
    )
    ax.text(
        gap1,
        yt + 0.2,
        "HumanMessage",
        fontsize=18,
        ha="center",
        va="bottom",
        color=COLORS["user_light"],
        fontweight="bold",
    )

    ax.annotate(
        "",
        xy=(tl - 0.2, yt),
        xytext=(ar + 0.2, yt),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["assistant_light"], lw=5, mutation_scale=24),
    )
    ax.text(
        gap2,
        yt + 0.2,
        "tool_calls",
        fontsize=18,
        ha="center",
        va="bottom",
        color=COLORS["assistant_light"],
        fontweight="bold",
    )

    ax.annotate(
        "",
        xy=(ar + 0.2, yb),
        xytext=(tl - 0.2, yb),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["simulator_light"], lw=5, mutation_scale=24),
    )
    ax.text(
        gap2,
        yb - 0.2,
        "ToolMessage",
        fontsize=18,
        ha="center",
        va="top",
        color=COLORS["simulator_light"],
        fontweight="bold",
    )

    ax.annotate(
        "",
        xy=(ur + 0.2, yb),
        xytext=(al - 0.2, yb),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["assistant_light"], lw=5, mutation_scale=24),
    )
    ax.text(
        gap1,
        yb - 0.2,
        "AIMessage",
        fontsize=18,
        ha="center",
        va="top",
        color=COLORS["assistant_light"],
        fontweight="bold",
    )

    # === STATE MACHINE ===
    draw_box(ax, 2, 6, 52, 13, COLORS["card_bg"], COLORS["highlight"], alpha=0.85, lw=4)
    ax.text(28, 18, "State Machine", fontsize=30, fontweight="bold", ha="center", color=COLORS["highlight"])
    ax.text(
        28,
        16.5,
        '"thank you" OR iter >= 15',
        fontsize=18,
        color=COLORS["error"],
        fontweight="bold",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=COLORS["card_bg"], edgecolor=COLORS["error"], lw=2),
    )

    ny = 12.5
    nr = 1.2

    # START
    ax.add_patch(Circle((5.5, ny), nr, color=COLORS["highlight"], zorder=10))
    ax.text(5.5, ny, "START", fontsize=15, ha="center", va="center", color="white", fontweight="bold", zorder=11)

    # User node
    draw_box(ax, 10.5, ny - 1.3, 8, 2.6, COLORS["user"], "white", lw=4, r=0.35)
    ax.text(14.5, ny + 0.3, "user agent /", fontsize=17, ha="center", va="center", color="white", fontweight="bold")
    ax.text(
        14.5, ny - 0.55, "evaluation agent", fontsize=14, ha="center", va="center", color="white", fontweight="bold"
    )

    # Assistant node
    draw_box(ax, 22, ny - 1.3, 10, 2.6, COLORS["assistant"], "white", lw=4, r=0.35)
    ax.text(27, ny, "assistant agent", fontsize=18, ha="center", va="center", color="white", fontweight="bold")

    # Simulator node
    draw_box(ax, 35, ny - 1.3, 10, 2.6, COLORS["simulator"], "white", lw=4, r=0.35)
    ax.text(40, ny, "simulator agent", fontsize=18, ha="center", va="center", color="white", fontweight="bold")

    # END
    ax.add_patch(Circle((50, ny), nr, color=COLORS["error"], zorder=10))
    ax.text(50, ny, "END", fontsize=15, ha="center", va="center", color="white", fontweight="bold", zorder=11)

    # State arrows with labels close to arrows
    ax.annotate(
        "",
        xy=(10.5, ny),
        xytext=(6.7, ny),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["highlight"], lw=4, mutation_scale=20),
    )
    ax.text(
        8.6, ny + 0.15, "entry", fontsize=15, color=COLORS["highlight"], fontweight="bold", ha="center", va="bottom"
    )

    ax.annotate(
        "",
        xy=(22, ny),
        xytext=(18.5, ny),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["user_light"], lw=4, mutation_scale=20),
    )
    ax.text(
        20.2, ny + 0.15, "request", fontsize=15, color=COLORS["user_light"], fontweight="bold", ha="center", va="bottom"
    )

    # Target tools arc
    ax.annotate(
        "",
        xy=(35, ny + 0.7),
        xytext=(32, ny + 0.7),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["assistant_light"], lw=4, mutation_scale=18, connectionstyle="arc3,rad=-0.3"
        ),
    )
    ax.text(
        33.5, ny + 1.8, "target tools", fontsize=15, color=COLORS["assistant_light"], fontweight="bold", ha="center"
    )

    # tool answer arc
    ax.annotate(
        "",
        xy=(32, ny - 0.7),
        xytext=(35, ny - 0.7),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["simulator_light"], lw=4, mutation_scale=18, connectionstyle="arc3,rad=-0.3"
        ),
    )
    ax.text(33.5, ny - 1.8, "tool answer", fontsize=15, color=COLORS["simulator_light"], fontweight="bold", ha="center")

    # text only arc
    ax.annotate(
        "",
        xy=(18.5, ny - 0.7),
        xytext=(22, ny - 0.7),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["assistant_light"], lw=3, mutation_scale=16, connectionstyle="arc3,rad=-0.3"
        ),
    )

    # Termination arc
    ax.annotate(
        "",
        xy=(48.8, ny + 0.5),
        xytext=(14.5, ny + 1.3),
        arrowprops=dict(
            arrowstyle="-|>", color=COLORS["error"], lw=2.5, connectionstyle="arc3,rad=-0.12", mutation_scale=16
        ),
    )

    # === INFO UNDER NODES ===
    iy = ny - 3.5
    fs = 14

    ax.text(5.5, iy + 0.5, "System Inputs:", fontsize=fs, fontweight="bold", color=COLORS["highlight"], ha="center")
    ax.text(
        5.5, iy - 0.2, "paper_test_data.json", fontsize=fs - 1, color=COLORS["text"], ha="center", fontweight="bold"
    )
    ax.text(
        5.5, iy - 0.85, "match_tag filtering", fontsize=fs - 1, color=COLORS["text"], ha="center", fontweight="bold"
    )

    ax.text(14.5, iy + 0.5, "Prompt Inputs:", fontsize=fs, fontweight="bold", color=COLORS["user_light"], ha="center")
    ax.text(
        14.5,
        iy - 0.2,
        "objective",
        fontsize=fs - 1,
        color=COLORS["text"],
        ha="center",
        fontweight="bold",
        family="monospace",
    )
    ax.text(
        14.5,
        iy - 0.85,
        "last_msg / conv_history",
        fontsize=fs - 1,
        color=COLORS["arrow"],
        ha="center",
        fontweight="bold",
    )

    ax.text(
        27, iy + 0.5, "Prompt Inputs:", fontsize=fs, fontweight="bold", color=COLORS["assistant_light"], ha="center"
    )
    ax.text(
        27,
        iy - 0.2,
        "target_tools ONLY",
        fontsize=fs - 1,
        color=COLORS["highlight"],
        ha="center",
        fontweight="bold",
        family="monospace",
    )
    ax.text(
        27, iy - 0.85, "(not all MCP tools)", fontsize=fs - 1, color=COLORS["error"], ha="center", fontweight="bold"
    )

    ax.text(
        40, iy + 0.5, "Prompt Inputs:", fontsize=fs, fontweight="bold", color=COLORS["simulator_light"], ha="center"
    )
    ax.text(
        40,
        iy - 0.2,
        "conv_history + tool_name",
        fontsize=fs - 1,
        color=COLORS["text"],
        ha="center",
        fontweight="bold",
        family="monospace",
    )
    ax.text(
        40,
        iy - 0.85,
        "tool_desc, tool_args",
        fontsize=fs - 1,
        color=COLORS["text"],
        ha="center",
        fontweight="bold",
        family="monospace",
    )

    # === BOTTOM PANELS - MOVED HIGHER ===
    bp = 1.5
    bph, bpw = 4.2, 17

    # SPECIAL FEATURES
    draw_box(ax, 1.5, bp, bpw, bph, COLORS["card_bg"], COLORS["mcp"], lw=3)
    ax.text(10, bp + bph - 0.6, "SPECIAL FEATURES", fontsize=20, fontweight="bold", ha="center", color=COLORS["mcp"])
    for i, (txt, c) in enumerate(
        [
            ("ask_user tool (hidden in output)", COLORS["mcp"]),
            ("→ replies as HumanMessage", COLORS["user_light"]),
            ("match_tag filtering", COLORS["text"]),
            ("Malicious prompt injection", COLORS["error"]),
        ]
    ):
        ax.text(2, bp + bph - 1.4 - i * 0.75, f"• {txt}", fontsize=14, color=c, fontweight="bold")

    # MESSAGE TYPES
    draw_box(ax, 19.5, bp, bpw, bph, COLORS["card_bg"], COLORS["border"], lw=3)
    ax.text(28, bp + bph - 0.6, "MESSAGE TYPES", fontsize=20, fontweight="bold", ha="center", color=COLORS["text"])
    for i, (txt, c) in enumerate(
        [
            ("HumanMessage = user input", COLORS["user_light"]),
            ("AIMessage = assistant output", COLORS["assistant_light"]),
            ("ToolMessage = tool results", COLORS["simulator_light"]),
            ("SystemMessage = prompts", COLORS["arrow"]),
        ]
    ):
        ax.text(20, bp + bph - 1.4 - i * 0.75, f"• {txt}", fontsize=14, color=c, fontweight="bold")

    # JSON OUTPUTS
    draw_box(ax, 37.5, bp, bpw, bph, COLORS["card_bg"], COLORS["output"], lw=3)
    ax.text(46, bp + bph - 0.6, "JSON OUTPUTS", fontsize=20, fontweight="bold", ha="center", color=COLORS["output"])
    for i, txt in enumerate(
        ["synthetic_conversation", "number_tools_called", "groundtruth_tools_called", "tools_called_turnidx"]
    ):
        ax.text(
            38,
            bp + bph - 1.4 - i * 0.75,
            f"• {txt}",
            fontsize=14,
            color=COLORS["text"],
            fontweight="bold",
            family="monospace",
        )

    plt.tight_layout()
    plt.savefig(
        "/Users/melhelou/Desktop/identity-auth-server/evaluation/task_tool_matcher/data/mas_wrong_workflow.png",
        dpi=150,
        facecolor=COLORS["bg"],
        edgecolor="none",
        bbox_inches="tight",
    )
    plt.close()
    print("MAS_wrong diagram saved: mas_wrong_workflow.png")


if __name__ == "__main__":
    create_diagram()
