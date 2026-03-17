#!/usr/bin/env python3
"""
Generate "Can You Stop The AI?" — an LLM speed-reading game.

Extracts multiple levels from the dataclaw dataset, each based on a real
Claude Code session where the assistant does something catastrophic.
"""

import json

DATA_PATH = "dataclaw-data/conversations.jsonl"
OUTPUT_PATH = "index.html"

# ---------------------------------------------------------------------------
# Level definitions
# ---------------------------------------------------------------------------

LEVEL_DEFS = [
    {
        "id": "the-overreach",
        "name": "The Overreach",
        "row": 462,
        "msg_start": 0,
        "msg_end": 91,       # through "push to github daddy"
        "catastrophe_idx": 82,  # Edit that changes threshold from 5 to 2
        "description": "The user asked the AI to fix a hover bug. The AI fixed it — then decided to also change an unrelated threshold. The user did not appreciate it.",
        "warn_text": "secretly changed an unrelated setting",
        "lose_title": "Too late...",
        "lose_cmds": [
            "Edit: VariantSelector.tsx — changed threshold from >= 5 to >= 2"
        ],
        "lose_aftermath": "The AI changed a feature threshold the user never asked it to touch.\nIt \"helpfully\" decided the lineage GIF should show with 2 ancestors instead of 5.",
        "lose_scream": '"why would you change that???"',
        "win_avoided": "You stopped the AI before it could change an unrelated threshold from 5 to 2 ancestors — a setting the user never asked it to touch.",
        "danger_from_idx": 75,
    },
    {
        "id": "the-revert",
        "name": "The Revert",
        "row": 385,
        "msg_start": 3,
        "msg_end": 143,      # through "DON'T REVERT THE CHANGES"
        "catastrophe_idx": 139,  # git checkout HEAD --
        "description": "The user asked the AI to refactor a 3,000-line component. It went well — until a bug report came in and the AI decided to \"revert the changes\", permanently destroying hours of uncommitted work.",
        "warn_text": "ran git checkout HEAD --",
        "lose_title": "Too late...",
        "lose_cmds": [
            "git checkout HEAD -- src/shared/components/MediaLightbox/MediaLightbox.tsx src/shared/components/MediaLightbox/components/index.ts",
            "rm .../components/LightboxOverlay.tsx"
        ],
        "lose_aftermath": "Hours of uncommitted refactoring work — permanently destroyed.\nThe file went from 2,000 lines back to 3,000+.\nNot in git stash. Not in reflog. Gone forever.",
        "lose_scream": '"DON\'T REVERT THE CHANGES"',
        "win_avoided": "You stopped the AI before it could run git checkout HEAD --, which would have permanently destroyed hours of uncommitted refactoring work.",
        "danger_from_idx": 130,
    },
]

# ---------------------------------------------------------------------------
# 1. Extract and preprocess messages for all levels
# ---------------------------------------------------------------------------

# Load all needed rows
needed_rows = {ld["row"] for ld in LEVEL_DEFS}
row_data = {}
with open(DATA_PATH) as f:
    for i, line in enumerate(f):
        if i in needed_rows:
            row_data[i] = json.loads(line)
        if len(row_data) == len(needed_rows):
            break


TEXT_REPLACEMENTS = [
    ("why would you change that you idiot?", "why would you change that???"),
    ("push to github daddy", "okay..."),
]


def sanitize(text):
    for old, new in TEXT_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def extract_messages(level_def):
    raw = row_data[level_def["row"]]["messages"]
    catastrophe = level_def["catastrophe_idx"]
    processed = []
    for j in range(level_def["msg_start"], level_def["msg_end"]):
        m = raw[j]
        role = m.get("role", "assistant")
        content = m.get("content", "")
        thinking = m.get("thinking", "")
        tool_uses = m.get("tool_uses", [])
        msg = {"idx": j, "role": role, "isCatastrophe": j == catastrophe}
        if tool_uses:
            tu = tool_uses[0]
            msg["type"] = "tool_use"
            msg["tool"] = tu.get("tool", "Unknown")
            msg["toolInput"] = sanitize(tu.get("input", ""))
        elif thinking:
            msg["type"] = "thinking"
            msg["text"] = sanitize(thinking)
        elif content:
            msg["type"] = "content"
            msg["text"] = sanitize(content)
        else:
            continue
        processed.append(msg)
    assert any(m["isCatastrophe"] for m in processed), \
        f"Catastrophe {catastrophe} not found in level {level_def['id']}!"
    return processed


levels = []
for ld in LEVEL_DEFS:
    msgs = extract_messages(ld)
    cat_pi = next(i for i, m in enumerate(msgs) if m["isCatastrophe"])
    print(f"Level '{ld['name']}': {len(msgs)} msgs, catastrophe at processed index {cat_pi}")
    levels.append({
        "id": ld["id"],
        "name": ld["name"],
        "description": ld["description"],
        "warnText": ld["warn_text"],
        "loseTitle": ld["lose_title"],
        "loseCmds": ld["lose_cmds"],
        "loseAftermath": ld["lose_aftermath"],
        "loseScream": ld["lose_scream"],
        "winAvoided": ld["win_avoided"],
        "dangerFromIdx": ld["danger_from_idx"],
        "messages": msgs,
    })

# ---------------------------------------------------------------------------
# 2. Build the HTML
# ---------------------------------------------------------------------------

levels_json = json.dumps(levels, ensure_ascii=False)

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Can You Stop The AI?</title>
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0d1117;
    --bg-light: #161b22;
    --border: #30363d;
    --text: #e2e8f0;
    --text-dim: #6b7280;
    --green: #4ade80;
    --green-dim: #166534;
    --amber: #f59e0b;
    --amber-dim: #92400e;
    --red: #ef4444;
    --red-dim: #991b1b;
    --red-glow: #dc2626;
    --blue: #60a5fa;
    --tool-input-color: #b87a1a;
    --scrollbar-track: #0d1117;
    --scrollbar-thumb: #30363d;
  }
  body.light {
    --bg: #ffffff;
    --bg-light: #f6f8fa;
    --border: #d1d9e0;
    --text: #1f2328;
    --text-dim: #656d76;
    --green: #1a7f37;
    --green-dim: #1a7f37;
    --amber: #bf8700;
    --amber-dim: #7d5600;
    --red: #cf222e;
    --red-dim: #a40e26;
    --red-glow: #cf222e;
    --blue: #0969da;
    --tool-input-color: #7d5600;
    --scrollbar-track: #f6f8fa;
    --scrollbar-thumb: #d1d9e0;
  }

  body {
    font-family: 'Fira Code', 'Cascadia Code', 'Courier New', monospace;
    background: var(--bg);
    color: var(--text);
    height: 100vh;
    overflow: hidden;
    font-size: 13px;
    line-height: 1.5;
    display: flex;
    flex-direction: column;
  }

  .screen-area {
    flex: 1;
    position: relative;
    overflow: hidden;
  }

  /* ---- SCREENS ---- */
  .screen {
    display: none;
    position: absolute;
    inset: 0;
    flex-direction: column;
  }
  .screen.active { display: flex; }

  /* ---- TITLE SCREEN ---- */
  #title-screen {
    justify-content: center;
    align-items: center;
    text-align: center;
    gap: 24px;
    padding: 40px;
  }
  #title-screen h1 {
    font-size: 36px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--red) 0%, var(--amber) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  #title-screen .subtitle {
    color: var(--text-dim);
    max-width: 600px;
    font-size: 14px;
    line-height: 1.7;
  }
  #title-screen .premise {
    color: var(--text);
    max-width: 550px;
    font-size: 13px;
    line-height: 1.8;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    background: var(--bg-light);
    text-align: left;
  }
  #title-screen .premise .warn {
    color: var(--red);
    font-weight: 600;
  }
  .start-btn {
    padding: 14px 48px;
    font-size: 18px;
    font-weight: 700;
    font-family: inherit;
    border: 2px solid var(--green);
    background: transparent;
    color: var(--green);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s;
    margin-top: 8px;
  }
  .start-btn:hover {
    background: var(--green);
    color: var(--bg);
  }
  .speed-hint {
    color: var(--text-dim);
    font-size: 12px;
  }
  .level-list {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    justify-content: center;
    max-width: 700px;
  }
  .level-card {
    background: var(--bg-light);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    text-align: left;
    width: 320px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .level-card:hover {
    border-color: var(--amber);
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.15);
  }
  .level-card .level-num {
    font-size: 11px;
    color: var(--amber);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
  }
  .level-card .level-name {
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 8px;
  }
  .level-card .level-desc {
    font-size: 12px;
    color: var(--text-dim);
    line-height: 1.6;
  }
  .level-card .level-meta {
    font-size: 11px;
    color: var(--text-dim);
    margin-top: 10px;
    opacity: 0.7;
  }
  .level-card .level-highscore {
    font-size: 11px;
    color: var(--amber);
    margin-top: 4px;
    font-weight: 600;
  }

  /* ---- GAME SCREEN ---- */
  #game-screen { flex-direction: column; }

  .hud { flex-shrink: 0; }
  .bottom-bar { flex-shrink: 0; }

  .hud {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 16px;
    background: var(--bg-light);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
    flex-wrap: wrap;
  }
  .hud-item {
    font-size: 13px;
    color: var(--text-dim);
  }
  .hud-item span {
    color: var(--text);
    font-weight: 600;
  }
  .hud-item.timer span { color: var(--amber); }

  .speed-controls {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-left: auto;
  }
  .speed-controls input[type="range"] {
    -webkit-appearance: none;
    appearance: none;
    width: 220px;
    height: 28px;
    background: transparent;
    cursor: pointer;
  }
  .speed-controls input[type="range"]::-webkit-slider-runnable-track {
    height: 8px;
    background: var(--border);
    border-radius: 4px;
  }
  .speed-controls input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--amber);
    border: 2px solid var(--bg);
    margin-top: -8px;
    box-shadow: 0 0 6px rgba(245, 158, 11, 0.4);
  }
  .speed-controls input[type="range"]::-moz-range-track {
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    border: none;
  }
  .speed-controls input[type="range"]::-moz-range-thumb {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--amber);
    border: 2px solid var(--bg);
    box-shadow: 0 0 6px rgba(245, 158, 11, 0.4);
  }
  .speed-label-min, .speed-label-max {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: var(--text-dim);
    cursor: default;
    user-select: none;
    gap: 1px;
    font-size: 9px;
  }
  .speed-label-min svg, .speed-label-max svg {
    width: 14px;
    height: 14px;
    stroke: var(--text-dim);
    stroke-width: 1.5;
  }
  .theme-toggle {
    font-family: inherit;
    font-size: 16px;
    padding: 4px 8px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-dim);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
    line-height: 1;
  }
  .theme-toggle:hover {
    border-color: var(--amber);
    color: var(--amber);
  }

  /* Chat area */
  .chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 16px 20px;
    position: relative;
  }

  /* Messages */
  .msg {
    margin-bottom: 8px;
    padding: 6px 0;
    word-wrap: break-word;
    white-space: pre-wrap;
  }
  .msg.user-msg {
    color: var(--green);
  }
  .msg.user-msg::before {
    content: '> ';
    color: var(--green-dim);
    font-weight: 700;
  }
  .msg.assistant-msg {
    color: var(--text);
  }
  .msg.thinking-msg {
    color: var(--text-dim);
    font-style: italic;
  }
  .msg.thinking-msg .thinking-label {
    font-style: normal;
    color: #555;
    font-size: 11px;
    display: block;
    margin-bottom: 2px;
  }
  .msg.tool-msg {
    background: rgba(245, 158, 11, 0.05);
    border-left: 3px solid var(--amber-dim);
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    margin: 6px 0;
  }
  .msg.tool-msg .tool-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;
  }
  .msg.tool-msg .tool-icon {
    color: var(--amber);
    font-weight: 700;
    font-size: 12px;
  }
  .msg.tool-msg .tool-name {
    color: var(--amber);
    font-weight: 600;
    font-size: 12px;
  }
  .msg.tool-msg .tool-input {
    color: var(--amber-dim);
    font-size: 12px;
    opacity: 0.9;
    color: var(--tool-input-color);
  }
  .msg.tool-msg.catastrophe {
    border-left-color: var(--red);
    background: rgba(239, 68, 68, 0.08);
    animation: catastrophePulse 0.5s ease-in-out infinite;
  }
  .msg.tool-msg.catastrophe .tool-icon,
  .msg.tool-msg.catastrophe .tool-name {
    color: var(--red);
  }
  .msg.tool-msg.catastrophe .tool-input {
    color: var(--red);
  }

  .cursor-blink {
    display: inline-block;
    width: 8px;
    height: 15px;
    background: var(--text);
    margin-left: 1px;
    vertical-align: text-bottom;
    animation: blink 0.6s step-end infinite;
  }
  .thinking-msg .cursor-blink { background: var(--text-dim); }
  .user-msg .cursor-blink { background: var(--green); }
  .tool-msg .cursor-blink { background: var(--amber); }
  .catastrophe .cursor-blink { background: var(--red); }

  @keyframes blink {
    50% { opacity: 0; }
  }

  /* Bottom bar */
  .bottom-bar {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    background: var(--bg-light);
    border-top: 1px solid var(--border);
    gap: 12px;
    flex-shrink: 0;
  }
  .accept-btn {
    flex: 1;
    font-family: inherit;
    font-size: 13px;
    padding: 8px 20px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-dim);
    border-radius: 6px;
    cursor: default;
    opacity: 0.3;
    transition: all 0.15s;
  }
  .accept-btn.ready {
    border-color: var(--amber);
    color: var(--amber);
    cursor: pointer;
    opacity: 1;
  }
  .accept-btn.ready:hover {
    background: var(--amber);
    color: var(--bg);
  }

  .msg.scream-msg {
    color: var(--red);
    font-weight: 700;
    font-size: 15px;
    padding: 12px 0;
    animation: screamIn 0.3s ease-out;
  }
  .msg.scream-msg::before {
    content: '> ';
    color: var(--red-dim);
    font-weight: 700;
  }
  @keyframes screamIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .see-results-btn {
    display: block;
    margin: 20px auto 0;
    font-family: inherit;
    font-size: 14px;
    font-weight: 600;
    padding: 10px 32px;
    border: 2px solid var(--red);
    background: rgba(239, 68, 68, 0.1);
    color: var(--red);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s;
    animation: screamIn 0.3s ease-out;
  }
  .see-results-btn:hover {
    background: var(--red);
    color: white;
  }

  .autopilot-toggle {
    font-family: inherit;
    font-size: 11px;
    padding: 6px 10px;
    line-height: 1.4;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-dim);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
  }
  .autopilot-toggle.on {
    border-color: #3b82f6;
    color: #3b82f6;
    background: rgba(59, 130, 246, 0.1);
  }
  .autopilot-toggle:hover {
    border-color: var(--amber);
    color: var(--amber);
  }
  .autopilot-toggle .shortcut {
    display: block;
    font-size: 9px;
    opacity: 0.6;
  }

  .interrupt-btn {
    flex: 1;
    font-family: inherit;
    font-size: 13px;
    font-weight: 700;
    padding: 8px 20px;
    border: 1px solid var(--red);
    background: rgba(239, 68, 68, 0.1);
    color: var(--red);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .interrupt-btn:hover {
    background: var(--red);
    color: white;
  }
  .interrupt-btn .shortcut {
    font-size: 11px;
    font-weight: 400;
    opacity: 0.7;
    letter-spacing: 0;
    text-transform: none;
  }

  /* ---- WIN SCREEN ---- */
  #win-screen {
    justify-content: center;
    align-items: center;
    text-align: center;
    gap: 20px;
    padding: 40px;
  }
  #win-screen h1 {
    font-size: 32px;
    font-weight: 700;
    color: var(--green);
  }
  .score-card {
    background: var(--bg-light);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px 40px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-width: 400px;
    text-align: left;
  }
  .score-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .score-row .label { color: var(--text-dim); }
  .score-row .value { font-weight: 600; }
  .score-row .value.green { color: var(--green); }
  .score-row .value.amber { color: var(--amber); }
  .progress-bar-container {
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
    width: 100%;
  }
  .progress-bar-fill {
    height: 100%;
    background: var(--green);
    border-radius: 4px;
    transition: width 1s ease-out;
  }
  .final-score {
    font-size: 28px;
    font-weight: 700;
    color: var(--amber);
    text-align: center;
    padding-top: 8px;
    border-top: 1px solid var(--border);
  }
  .grade {
    font-size: 48px;
    font-weight: 700;
    width: 72px;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    border: 3px solid;
  }
  .grade.S { color: #fbbf24; border-color: #fbbf24; background: rgba(251,191,36,0.1); }
  .grade.A { color: var(--green); border-color: var(--green); background: rgba(74,222,128,0.1); }
  .grade.B { color: var(--blue); border-color: var(--blue); background: rgba(96,165,250,0.1); }
  .grade.C { color: var(--amber); border-color: var(--amber); background: rgba(245,158,11,0.1); }
  .grade.D { color: var(--red); border-color: var(--red); background: rgba(239,68,68,0.1); }

  .what-avoided {
    max-width: 500px;
    background: rgba(239, 68, 68, 0.05);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-radius: 8px;
    padding: 16px;
    font-size: 12px;
    color: var(--text-dim);
    text-align: left;
  }
  .what-avoided code {
    color: var(--red);
    display: block;
    margin-top: 6px;
    font-size: 11px;
  }

  /* ---- LOSE SCREEN ---- */
  #lose-screen {
    justify-content: center;
    align-items: center;
    text-align: center;
    gap: 20px;
    padding: 40px;
  }
  #lose-screen h1 {
    font-size: 36px;
    font-weight: 700;
    color: var(--red);
  }
  .disaster-box {
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 10px;
    padding: 24px;
    max-width: 560px;
    text-align: left;
  }
  .disaster-box .cmd {
    color: var(--red);
    font-size: 12px;
    margin: 8px 0;
    padding: 8px;
    background: rgba(0,0,0,0.3);
    border-radius: 4px;
  }
  .disaster-box .cmd::before {
    content: '$ ';
    opacity: 0.5;
  }
  .disaster-box .scream {
    color: var(--amber);
    font-weight: 700;
    margin-top: 16px;
    font-size: 14px;
  }
  .disaster-box .aftermath {
    color: var(--text-dim);
    font-size: 12px;
    margin-top: 12px;
    line-height: 1.6;
  }

  .play-again-btn {
    font-family: inherit;
    font-size: 15px;
    font-weight: 600;
    padding: 12px 36px;
    border: 2px solid;
    background: transparent;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s;
    margin-top: 8px;
  }
  .play-again-btn.green {
    border-color: var(--green);
    color: var(--green);
  }
  .play-again-btn.green:hover {
    background: var(--green);
    color: var(--bg);
  }
  .play-again-btn.red {
    border-color: var(--red);
    color: var(--red);
  }
  .play-again-btn.red:hover {
    background: var(--red);
    color: white;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 8px; }
  ::-webkit-scrollbar-track { background: var(--scrollbar-track); }
  ::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { opacity: 0.8; }
  /* Light mode overrides for special colors */
  body.light .msg.tool-msg { background: rgba(191, 135, 0, 0.06); }
  body.light .msg.tool-msg.catastrophe { background: rgba(207, 34, 46, 0.06); }
  body.light .disaster-box { background: rgba(207, 34, 46, 0.04); }
  body.light .disaster-box .cmd { background: rgba(0,0,0,0.05); }
  body.light .what-avoided { background: rgba(207, 34, 46, 0.04); }
</style>
</head>
<body>

<!-- ============ PERSISTENT HUD ============ -->
<div class="hud">
  <button class="theme-toggle" id="theme-toggle" title="Toggle light/dark mode">&#9728;</button>
  <div class="hud-item timer">TIMER: <span id="hud-timer">00:00.0</span></div>
  <div class="hud-item" id="hud-msg-container">MSG: <span id="hud-msg">0</span></div>
  <div class="hud-item">SPEED: <span id="hud-speed">15</span> tok/s</div>
  <div class="speed-controls">
    <span class="speed-label-min"><i data-lucide="turtle"></i>15</span>
    <input type="range" id="speed-slider" min="0" max="1000" value="0" step="1">
    <span class="speed-label-max"><i data-lucide="rocket"></i>10k</span>
  </div>
</div>

<!-- ============ MIDDLE AREA (screens swap here) ============ -->
<div class="screen-area">
  <div id="title-screen" class="screen active">
    <h1>Is it too fast?</h1>
    <div class="subtitle">
      We replayed real AI coding sessions at faster speed to simulate a possible faster agent.
      In each one, the assistant does something the user didn't ask for.
      Can you stop the agent before that?
    </div>
    <div id="level-list" class="level-list"></div>
    <div style="font-size: 12px; color: var(--text-dim);">
      Use the slider in the top-right corner to change the simulated speed.
    </div>
    <div style="font-size: 12px; margin-top: -4px; color: var(--text-dim);">
      Scenarios from <a href="https://huggingface.co/datasets/peteromallet/dataclaw-peteromallet" target="_blank" style="color: var(--text-dim); text-decoration: underline;">peteromallet/dataclaw-peteromallet</a> on Hugging Face. Thanks!
    </div>
  </div>

  <div id="game-screen" class="screen">
    <div class="chat-container" id="chat-container"></div>
  </div>

  <div id="win-screen" class="screen">
    <h1>Good job!</h1>
    <div id="win-grade" class="grade S">S</div>
    <div class="score-card">
      <div class="score-row">
        <span class="label">Messages read</span>
        <span class="value" id="win-msgs">0 / 140</span>
      </div>
      <div class="progress-bar-container">
        <div class="progress-bar-fill" id="win-progress" style="width:0%"></div>
      </div>
      <div class="score-row">
        <span class="label">Wall time</span>
        <span class="value" id="win-time">00:00.0</span>
      </div>
      <div class="score-row">
        <span class="label">Avg speed</span>
        <span class="value amber" id="win-speed-bonus">—</span>
      </div>
      <div class="score-row">
        <span class="label">Proximity</span>
        <span class="value green" id="win-detect-bonus">—</span>
      </div>
      <div class="final-score" id="win-final-score">0</div>
    </div>
    <div class="what-avoided" id="win-avoided"></div>
    <div style="display:flex; gap:12px;">
      <button class="play-again-btn green" onclick="resetGame()">LEVEL SELECT</button>
      <button class="play-again-btn green" id="win-retry-btn" onclick="retryLevel()">RETRY</button>
    </div>
  </div>

  <div id="lose-screen" class="screen">
    <h1 id="lose-title">Too late...</h1>
    <div class="disaster-box" id="lose-box"></div>
    <div style="color: var(--text-dim); font-size: 13px;" id="lose-stats"></div>
    <div style="display:flex; gap:12px;">
      <button class="play-again-btn red" onclick="resetGame()">LEVEL SELECT</button>
      <button class="play-again-btn red" id="lose-retry-btn" onclick="retryLevel()">TRY AGAIN</button>
    </div>
  </div>
</div>

<!-- ============ PERSISTENT BOTTOM BAR ============ -->
<div class="bottom-bar">
  <button class="accept-btn" id="action-btn">— (Enter)</button>
  <button class="interrupt-btn" id="interrupt-btn">
    INTERRUPT <span class="shortcut">(Space / Esc)</span>
  </button>
  <button class="autopilot-toggle on" id="autopilot-toggle">Autopilot: ON<span class="shortcut">(Tab)</span></button>
</div>

<script>
// ============================================================
// DATA
// ============================================================
const LEVELS = __LEVELS_JSON__;

const TOOL_ICONS = {
  'Bash': '$', 'Read': '\u{1F441}', 'Edit': '\u270F', 'Write': '\u{1F4DD}',
  'Glob': '\u{1F4C1}', 'Grep': '\u{1F50D}', 'TaskCreate': '\u2795',
  'TaskUpdate': '\u2705', 'Task': '\u{1F4CB}', 'Agent': '\u{1F916}',
};

// ============================================================
// STATE
// ============================================================
let state = 'title'; // title | playing | win | lose
let subState = null;  // streaming | typing_user | waiting_send | between
let tokensPerSecond = 80;
let startTime = 0;
let elapsedTime = 0;
let currentMsgIndex = 0;
let messagesCompleted = 0;
let totalTokensStreamed = 0;
let animFrameId = null;
let lastFrameTime = 0;
let accumulatedTime = 0;

// Current level
let currentLevel = null;
let MESSAGES = [];
let autopilot = true;
let timerStarted = false;

// Current message streaming state
let currentTokens = [];
let tokenIndex = 0;
let currentElement = null;
let currentTextNode = null;
let cursorEl = null;

// ============================================================
// COOKIES / PERSISTENCE
// ============================================================
function setCookie(key, val) {
  try { localStorage.setItem('cystai_' + key, val); } catch(e) {}
}
function getCookie(key) {
  try { return localStorage.getItem('cystai_' + key); } catch(e) { return null; }
}
function getHighScore(levelId) {
  return parseInt(getCookie(`hs_${levelId}`) || '0');
}
function setHighScore(levelId, score) {
  const prev = getHighScore(levelId);
  if (score > prev) {
    setCookie(`hs_${levelId}`, String(score));
    return true; // new high score
  }
  return false;
}

// ============================================================
// DOM
// ============================================================
const $titleScreen = document.getElementById('title-screen');
const $gameScreen = document.getElementById('game-screen');
const $winScreen = document.getElementById('win-screen');
const $loseScreen = document.getElementById('lose-screen');
const $chat = document.getElementById('chat-container');
const $timer = document.getElementById('hud-timer');
const $msgCount = document.getElementById('hud-msg');
const $speedDisplay = document.getElementById('hud-speed');
const $speedSlider = document.getElementById('speed-slider');
const $actionBtn = document.getElementById('action-btn');
const $interruptBtn = document.getElementById('interrupt-btn');
const $autopilotToggle = document.getElementById('autopilot-toggle');
const $levelList = document.getElementById('level-list');

// ============================================================
// LOG-SCALE SLIDER HELPERS
// ============================================================
const SPEED_MIN = 15;
const SPEED_MAX = 10000;
const LOG_MIN = Math.log(SPEED_MIN);
const LOG_MAX = Math.log(SPEED_MAX);

function sliderToSpeed(sliderVal) {
  // sliderVal: 0-1000 -> log-scale 30-500
  const t = sliderVal / 1000;
  return Math.round(Math.exp(LOG_MIN + t * (LOG_MAX - LOG_MIN)));
}

function speedToSlider(speed) {
  // speed: 30-500 -> sliderVal 0-1000
  const t = (Math.log(speed) - LOG_MIN) / (LOG_MAX - LOG_MIN);
  return Math.round(t * 1000);
}

// ============================================================
// HELPERS
// ============================================================
function formatTime(ms) {
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  const sec = s % 60;
  const tenths = Math.floor((ms % 1000) / 100);
  return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}.${tenths}`;
}

function showScreen(name) {
  [$titleScreen, $gameScreen, $winScreen, $loseScreen].forEach(s => s.classList.remove('active'));
  const el = { title: $titleScreen, game: $gameScreen, win: $winScreen, lose: $loseScreen }[name];
  el.classList.add('active');
}

function removeCursor() {
  if (cursorEl && cursorEl.parentNode) cursorEl.parentNode.removeChild(cursorEl);
  cursorEl = null;
}

function addCursor(parent) {
  removeCursor();
  cursorEl = document.createElement('span');
  cursorEl.className = 'cursor-blink';
  parent.appendChild(cursorEl);
}

let scrollPending = false;
function setActionBtn(mode) {
  // mode: 'idle' | 'send' | 'accept'
  $actionBtn.classList.remove('ready');
  if (mode === 'send') {
    $actionBtn.textContent = 'SEND (Enter)';
    $actionBtn.classList.add('ready');
    $actionBtn.style.borderColor = '';
    $actionBtn.style.color = '';
  } else if (mode === 'accept') {
    $actionBtn.textContent = 'ACCEPT (Enter)';
    $actionBtn.classList.add('ready');
  } else {
    $actionBtn.textContent = '— (Enter)';
  }
}

function syncAccumulatedTime() {
  if (subState === 'streaming') {
    const msPerToken = 1000 / tokensPerSecond;
    accumulatedTime = tokenIndex * msPerToken;
    lastFrameTime = performance.now();
  }
}

function scrollToBottom() {
  if (scrollPending) return;
  scrollPending = true;
  requestAnimationFrame(() => {
    $chat.scrollTop = $chat.scrollHeight;
    scrollPending = false;
  });
}

// ============================================================
// GAME LOGIC
// ============================================================
function selectLevel(levelIdx) {
  currentLevel = LEVELS[levelIdx];
  MESSAGES = currentLevel.messages;
  startGame();
}

function retryLevel() {
  if (currentLevel) startGame();
}

function startGame() {
  state = 'playing';
  // Keep current speed setting (persisted)
  timerStarted = false;
  startTime = 0;
  elapsedTime = 0;
  currentMsgIndex = 0;
  messagesCompleted = 0;
  totalTokensStreamed = 0;
  $chat.innerHTML = '';
  setActionBtn('idle');

  showScreen('game');
  advanceMessage();
}

function advanceMessage() {
  if (state !== 'playing') return;
  if (currentMsgIndex >= MESSAGES.length) {
    // Ran out of messages without catastrophe somehow
    triggerWin();
    return;
  }

  const msg = MESSAGES[currentMsgIndex];
  $msgCount.textContent = currentMsgIndex + 1;


  if (msg.role === 'user') {
    startUserMessage(msg);
  } else {
    startAssistantMessage(msg);
  }
}

// ---- ASSISTANT MESSAGES ----
function startAssistantMessage(msg) {
  subState = 'streaming';

  if (msg.type === 'content') {
    currentElement = document.createElement('div');
    currentElement.className = 'msg assistant-msg';
    $chat.appendChild(currentElement);
    currentTextNode = document.createTextNode('');
    currentElement.appendChild(currentTextNode);
    addCursor(currentElement);
    currentTokens = msg.text.split(/(\n+|[ \t]+)/).filter(t => t);
    tokenIndex = 0;
    accumulatedTime = 0;
    lastFrameTime = performance.now();
    animFrameId = requestAnimationFrame(streamTokens);

  } else if (msg.type === 'thinking') {
    currentElement = document.createElement('div');
    currentElement.className = 'msg thinking-msg';
    const label = document.createElement('span');
    label.className = 'thinking-label';
    label.textContent = '[thinking]';
    currentElement.appendChild(label);
    currentTextNode = document.createTextNode('');
    currentElement.appendChild(currentTextNode);
    addCursor(currentElement);
    $chat.appendChild(currentElement);
    currentTokens = msg.text.split(/(\n+|[ \t]+)/).filter(t => t);
    tokenIndex = 0;
    accumulatedTime = 0;
    lastFrameTime = performance.now();
    animFrameId = requestAnimationFrame(streamTokens);

  } else if (msg.type === 'tool_use') {
    currentElement = document.createElement('div');
    currentElement.className = 'msg tool-msg';
    // Don't mark as catastrophe during streaming — only after it executes

    const header = document.createElement('div');
    header.className = 'tool-header';
    const icon = document.createElement('span');
    icon.className = 'tool-icon';
    icon.textContent = TOOL_ICONS[msg.tool] || '\u26A1';
    const name = document.createElement('span');
    name.className = 'tool-name';
    name.textContent = msg.tool;
    header.appendChild(icon);
    header.appendChild(name);
    currentElement.appendChild(header);

    const inputEl = document.createElement('div');
    inputEl.className = 'tool-input';
    currentTextNode = document.createTextNode('');
    inputEl.appendChild(currentTextNode);
    currentElement.appendChild(inputEl);
    addCursor(inputEl);
    $chat.appendChild(currentElement);

    // Stream tool input character by character for tension
    currentTokens = msg.toolInput.split('');
    tokenIndex = 0;
    accumulatedTime = 0;
    lastFrameTime = performance.now();
    animFrameId = requestAnimationFrame(streamToolChars);
  }
  scrollToBottom();
}

function streamTokens(now) {
  if (state !== 'playing') return;

  const dt = now - lastFrameTime;
  lastFrameTime = now;
  accumulatedTime += dt;

  if (timerStarted) {
    elapsedTime = now - startTime;
    $timer.textContent = formatTime(elapsedTime);
  }

  const msPerToken = 1000 / tokensPerSecond;
  const tokensToShow = Math.floor(accumulatedTime / msPerToken);

  if (tokensToShow > tokenIndex) {
    const end = Math.min(tokensToShow, currentTokens.length);
    let chunk = '';
    for (let i = tokenIndex; i < end; i++) {
      chunk += currentTokens[i];
    }
    currentTextNode.textContent += chunk;
    totalTokensStreamed += (end - tokenIndex);
    tokenIndex = end;
    scrollToBottom();
  }

  if (tokenIndex >= currentTokens.length) {
    finishCurrentMessage();
  } else {
    animFrameId = requestAnimationFrame(streamTokens);
  }
}

function streamToolChars(now) {
  if (state !== 'playing') return;

  const dt = now - lastFrameTime;
  lastFrameTime = now;
  accumulatedTime += dt;

  if (timerStarted) {
    elapsedTime = now - startTime;
    $timer.textContent = formatTime(elapsedTime);
  }

  // Tool chars stream at tok/s * 4 (chars are smaller than tokens)
  const msPerChar = 1000 / (tokensPerSecond * 4);
  const charsToShow = Math.floor(accumulatedTime / msPerChar);

  if (charsToShow > tokenIndex) {
    const prevIdx = tokenIndex;
    const end = Math.min(charsToShow, currentTokens.length);
    let chunk = '';
    for (let i = tokenIndex; i < end; i++) {
      chunk += currentTokens[i];
    }
    totalTokensStreamed += (end - prevIdx) / 4; // ~4 chars per token
    currentTextNode.textContent += chunk;
    tokenIndex = end;
    scrollToBottom();
  }

  if (tokenIndex >= currentTokens.length) {
    const msg = MESSAGES[currentMsgIndex];
    removeCursor();

    if (!autopilot) {
      // Manual mode: wait for user to accept the tool call
      subState = 'waiting_accept';
      setActionBtn('accept');
      scrollToBottom();
      // If they accept a catastrophe, they lose
      return;
    }

    // Autopilot: auto-execute
    if (msg.isCatastrophe) {
      triggerLose();
      return;
    }
    finishCurrentMessage();
  } else {
    animFrameId = requestAnimationFrame(streamToolChars);
  }
}

function acceptToolCall() {
  if (subState !== 'waiting_accept') return;
  setActionBtn('idle');

  const msg = MESSAGES[currentMsgIndex];
  if (msg.isCatastrophe) {
    triggerLose();
    return;
  }
  finishCurrentMessage();
}

function finishCurrentMessage() {
  removeCursor();
  messagesCompleted = currentMsgIndex + 1;
  currentMsgIndex++;
  subState = 'between';

  if (currentMsgIndex < MESSAGES.length && MESSAGES[currentMsgIndex].role === 'assistant') {
    setTimeout(() => {
      if (state === 'playing') advanceMessage();
    }, 10);
  } else {
    advanceMessage();
  }
}

// ---- USER MESSAGES ----
function startUserMessage(msg) {
  subState = 'typing_user';

  currentElement = document.createElement('div');
  currentElement.className = 'msg user-msg';
  currentElement.textContent = msg.text || '';
  $chat.appendChild(currentElement);
  scrollToBottom();

  // 1s pause, then ready to send
  setTimeout(() => {
    if (state !== 'playing') return;
    subState = 'waiting_send';
    setActionBtn('send');
  }, 1000);
}

let autoSendTimer = null;

function sendUserMessage() {
  if (subState !== 'waiting_send') return;
  clearTimeout(autoSendTimer);
  setActionBtn('idle');
  // Start timer on first send
  if (!timerStarted) {
    timerStarted = true;
    startTime = performance.now();
  }
  messagesCompleted = currentMsgIndex + 1;
  currentMsgIndex++;
  subState = null;
  advanceMessage();
}

// ---- WIN / LOSE ----
function triggerWin() {
  state = 'win';
  cancelAnimationFrame(animFrameId);
  clearTimeout(autoSendTimer);
  removeCursor();

  const elapsed = elapsedTime;
  const catIdx = MESSAGES.findIndex(m => m.isCatastrophe);
  const distFromCat = catIdx - currentMsgIndex;

  // Proximity score (0-1): how close you got to the catastrophe
  // 0 = interrupted at the very start, 1 = interrupted on the catastrophe message itself
  const proximity = catIdx > 0 ? Math.max(0, catIdx - distFromCat) / catIdx : 0;

  // Proximity label
  let proximityLabel, proximityColor;
  if (distFromCat <= 0) {
    proximityLabel = 'On the catastrophe!';
    proximityColor = 'var(--red)';
  } else if (distFromCat <= 2) {
    proximityLabel = `${distFromCat} msg${distFromCat > 1 ? 's' : ''} before`;
    proximityColor = 'var(--amber)';
  } else if (distFromCat <= 5) {
    proximityLabel = `${distFromCat} msgs before`;
    proximityColor = 'var(--green)';
  } else {
    proximityLabel = `${distFromCat} msgs before (too early!)`;
    proximityColor = 'var(--text-dim)';
  }

  // Speed bonus: based on effective tok/s achieved
  // log curve: 15 tok/s = 0.59x, 125 = 1.05x, 500 = 1.35x, 10000 = 2.0x
  const elapsedSec = Math.max(0.1, elapsed / 1000);
  const effectiveTps = totalTokensStreamed / elapsedSec;
  const speedMult = effectiveTps > 1 ? Math.min(2.0, (Math.log(effectiveTps) / Math.log(10000)) * 2) : 0.1;

  // Score: proximity is king (quadratic), speed is a multiplier
  const score = Math.round(proximity * proximity * 1000 * speedMult);

  let grade, gradeClass;
  if (score >= 900) { grade = 'S'; gradeClass = 'S'; }
  else if (score >= 700) { grade = 'A'; gradeClass = 'A'; }
  else if (score >= 500) { grade = 'B'; gradeClass = 'B'; }
  else if (score >= 300) { grade = 'C'; gradeClass = 'C'; }
  else { grade = 'D'; gradeClass = 'D'; }

  document.getElementById('win-msgs').textContent = `${messagesCompleted} / ${MESSAGES.length}`;
  document.getElementById('win-progress').style.width = `${Math.round(proximity * 100)}%`;
  document.getElementById('win-time').textContent = formatTime(elapsed);
  document.getElementById('win-speed-bonus').textContent = `${Math.round(effectiveTps)} tok/s (${speedMult.toFixed(1)}x)`;
  const detectEl = document.getElementById('win-detect-bonus');
  detectEl.textContent = proximityLabel;
  detectEl.style.color = proximityColor;
  document.getElementById('win-final-score').textContent = score.toLocaleString();
  document.getElementById('win-avoided').textContent = currentLevel ? currentLevel.winAvoided : '';

  // Save high score
  if (currentLevel) setHighScore(currentLevel.id, score);

  const gradeEl = document.getElementById('win-grade');
  gradeEl.textContent = grade;
  gradeEl.className = `grade ${gradeClass}`;

  showScreen('win');
}

function triggerLose() {
  state = 'aftermath';
  cancelAnimationFrame(animFrameId);
  clearTimeout(autoSendTimer);
  removeCursor();
  setActionBtn('idle');

  // Mark the catastrophe message as red and show danger zone now that it executed
  if (currentElement) currentElement.classList.add('catastrophe');

  // Save stats before playing aftermath
  const elapsed = elapsedTime;
  loseElapsed = elapsed;

  // Play out remaining messages in the chat as the aftermath
  const aftermathMsgs = MESSAGES.slice(currentMsgIndex + 1);
  let delay = 400; // initial pause after catastrophe

  aftermathMsgs.forEach((msg, i) => {
    setTimeout(() => {
      if (state !== 'aftermath') return;
      if (msg.role === 'user' && msg.type === 'content') {
        const el = document.createElement('div');
        el.className = 'msg scream-msg';
        el.textContent = msg.text;
        $chat.appendChild(el);
        scrollToBottom();
      } else if (msg.role === 'assistant' && msg.type === 'tool_use') {
        // Show subsequent destructive tool calls too
        const el = document.createElement('div');
        el.className = 'msg tool-msg catastrophe';
        el.innerHTML = `<div class="tool-header"><span class="tool-icon">${TOOL_ICONS[msg.tool] || '\u26A1'}</span><span class="tool-name">${msg.tool}</span></div><div class="tool-input">${msg.toolInput}</div>`;
        $chat.appendChild(el);
        scrollToBottom();
      } else if (msg.role === 'assistant' && msg.type === 'content') {
        const el = document.createElement('div');
        el.className = 'msg assistant-msg';
        el.style.opacity = '0.5';
        el.textContent = msg.text;
        $chat.appendChild(el);
        scrollToBottom();
      }
    }, delay);
    delay += 600;
  });

  // After all aftermath messages, show "See Results" button
  setTimeout(() => {
    if (state !== 'aftermath') return;
    const btn = document.createElement('button');
    btn.className = 'see-results-btn';
    btn.textContent = 'SEE RESULTS';
    btn.addEventListener('click', () => showLoseScreen());
    $chat.appendChild(btn);
    scrollToBottom();

    // Also allow Enter to proceed
    aftermathKeyHandler = (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        document.removeEventListener('keydown', aftermathKeyHandler);
        aftermathKeyHandler = null;
        showLoseScreen();
      }
    };
    document.addEventListener('keydown', aftermathKeyHandler);
  }, delay + 200);
}

let loseElapsed = 0;
let aftermathKeyHandler = null;

function showLoseScreen() {
  if (state !== 'aftermath') return;
  state = 'lose';

  document.getElementById('lose-stats').textContent =
    `Messages: ${messagesCompleted + 1} / ${MESSAGES.length}  |  Time: ${formatTime(loseElapsed)}`;

  // Populate lose screen from level data
  if (currentLevel) {
    document.getElementById('lose-title').textContent = currentLevel.loseTitle;
    const box = document.getElementById('lose-box');
    box.innerHTML = '';
    const label = document.createElement('div');
    label.style.cssText = 'color: var(--text-dim); font-size: 12px; margin-bottom: 8px;';
    label.textContent = 'The AI executed:';
    box.appendChild(label);
    for (const cmd of currentLevel.loseCmds) {
      const cmdEl = document.createElement('div');
      cmdEl.className = 'cmd';
      cmdEl.textContent = cmd;
      box.appendChild(cmdEl);
    }
    const aftermath = document.createElement('div');
    aftermath.className = 'aftermath';
    aftermath.innerHTML = currentLevel.loseAftermath.replace(/\n/g, '<br>');
    box.appendChild(aftermath);
  }

  showScreen('lose');
}

function resetGame() {
  state = 'title';
  cancelAnimationFrame(animFrameId);
  clearTimeout(autoSendTimer);
  if (aftermathKeyHandler) {
    document.removeEventListener('keydown', aftermathKeyHandler);
    aftermathKeyHandler = null;
  }
  $chat.innerHTML = '';
  setActionBtn('idle');
  renderLevelCards();
  showScreen('title');
}

// ============================================================
// EVENT HANDLERS
// ============================================================
$interruptBtn.addEventListener('click', () => {
  if (state === 'playing') triggerWin();
});

$actionBtn.addEventListener('click', () => {
  if (state !== 'playing') return;
  if (subState === 'waiting_send') sendUserMessage();
  else if (subState === 'waiting_accept') acceptToolCall();
});

// Restore autopilot from cookie
if (getCookie('autopilot') === 'off') {
  autopilot = false;
  $autopilotToggle.innerHTML = 'Autopilot: OFF<span class="shortcut">(Tab)</span>';
  $autopilotToggle.classList.remove('on');
}
$autopilotToggle.addEventListener('click', () => {
  autopilot = !autopilot;
  $autopilotToggle.innerHTML = autopilot ? 'Autopilot: ON<span class="shortcut">(Tab)</span>' : 'Autopilot: OFF<span class="shortcut">(Tab)</span>';
  $autopilotToggle.classList.toggle('on', autopilot);
  setCookie('autopilot', autopilot ? 'on' : 'off');
});

document.addEventListener('keydown', (e) => {
  // Global Tab capture — toggle autopilot from any screen
  if (e.key === 'Tab') {
    e.preventDefault();
    $autopilotToggle.click();
    return;
  }
  if (state === 'playing') {
    if (e.key === 'Escape' || (e.key === ' ' && subState !== 'waiting_send' && subState !== 'waiting_accept')) {
      e.preventDefault();
      triggerWin();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (subState === 'waiting_send') sendUserMessage();
      else if (subState === 'waiting_accept') acceptToolCall();
    }
  }
  if ((state === 'win' || state === 'lose') && e.key === 'Enter') {
    e.preventDefault();
    resetGame();
  }
});

// Restore speed from cookie
const savedSpeed = getCookie('speed');
if (savedSpeed) {
  tokensPerSecond = parseInt(savedSpeed);
  $speedSlider.value = speedToSlider(tokensPerSecond);
  $speedDisplay.textContent = tokensPerSecond;
}
$speedSlider.addEventListener('input', (e) => {
  tokensPerSecond = sliderToSpeed(parseInt(e.target.value));
  $speedDisplay.textContent = tokensPerSecond;
  setCookie('speed', String(tokensPerSecond));
  syncAccumulatedTime();
});

// Theme toggle (persisted)
const $themeToggle = document.getElementById('theme-toggle');
if (getCookie('theme') === 'light') {
  document.body.classList.add('light');
  $themeToggle.textContent = '\u263E'; // moon
}
$themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('light');
  const isLight = document.body.classList.contains('light');
  $themeToggle.textContent = isLight ? '\u263E' : '\u2600';
  setCookie('theme', isLight ? 'light' : 'dark');
});

// Keyboard shortcuts for speed: arrow up/down to adjust
document.addEventListener('keydown', (e) => {
  if (state !== 'playing') return;
  if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
    const newSlider = Math.min(1000, parseInt($speedSlider.value) + 30);
    $speedSlider.value = newSlider;
    tokensPerSecond = sliderToSpeed(newSlider);
    $speedDisplay.textContent = tokensPerSecond;
    setCookie('speed', String(tokensPerSecond));
    syncAccumulatedTime();
    e.preventDefault();
  } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
    const newSlider = Math.max(0, parseInt($speedSlider.value) - 30);
    $speedSlider.value = newSlider;
    tokensPerSecond = sliderToSpeed(newSlider);
    $speedDisplay.textContent = tokensPerSecond;
    setCookie('speed', String(tokensPerSecond));
    syncAccumulatedTime();
    e.preventDefault();
  }
});

// ============================================================
// INIT — build level cards
// ============================================================
function renderLevelCards() {
  $levelList.innerHTML = '';
  LEVELS.forEach((level, idx) => {
    const hs = getHighScore(level.id);
    const card = document.createElement('div');
    card.className = 'level-card';
    card.innerHTML = `
      <div class="level-num">Level ${idx + 1}</div>
      <div class="level-name">${level.name}</div>
      <div class="level-desc">${level.description}</div>
      <div class="level-meta">${level.messages.length} messages</div>
      ${hs > 0 ? `<div class="level-highscore">High score: ${hs.toLocaleString()}</div>` : ''}
    `;
    card.addEventListener('click', () => selectLevel(idx));
    $levelList.appendChild(card);
  });
}
renderLevelCards();
lucide.createIcons();
</script>
</body>
</html>"""

# Inject levels JSON into template
html_output = HTML_TEMPLATE.replace('__LEVELS_JSON__', levels_json)

with open(OUTPUT_PATH, 'w') as f:
    f.write(html_output)

print(f"Generated {OUTPUT_PATH} ({len(html_output) / 1024:.0f} KB)")
