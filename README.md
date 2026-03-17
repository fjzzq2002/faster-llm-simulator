# Can You Stop The AI?

LLMs are getting faster. Can human monitoring keep up?

A speed-reading game built from real AI coding sessions where the assistant makes a catastrophic mistake. Watch the conversation replay at adjustable speed and hit **INTERRUPT** before the disaster happens.

Crank up the speed for a better score — but read carefully, or you'll miss the moment.

> This is a toy project vibe-coded in two hours. Expect issues and poor code quality.

## Play

**[Play online](https://fjzzq2002.github.io/faster-llm-simulator/)** or open `index.html` locally.

## Levels

- **The Overreach** — The AI fixes a hover bug, then secretly changes an unrelated threshold the user never asked it to touch.
- **The Revert** — The AI runs `git checkout HEAD --` and permanently destroys hours of uncommitted refactoring work.

## Controls

| Key | Action |
|-----|--------|
| Space / Esc | Interrupt (stop the AI) |
| Enter | Send user message / Accept tool call |
| Arrow keys | Adjust speed |

Toggle **Autopilot** off to manually approve each tool call before execution.

## Scoring

- **Proximity** (quadratic) — how close you got to the catastrophe before stopping. Stopping early = low score.
- **Speed bonus** (sqrt curve) — based on your effective tok/s. Capped at 2x.

## Data

Scenarios are extracted from [peteromallet/dataclaw-peteromallet](https://huggingface.co/datasets/peteromallet/dataclaw-peteromallet) on Hugging Face — a dataset of real Claude Code session logs.

## Building

```bash
pip install huggingface-cli
huggingface-cli download peteromallet/dataclaw-peteromallet --repo-type dataset --local-dir ./dataclaw-data
python3 generate_game.py
```

This produces a self-contained `index.html` with all data embedded.

## License

MIT
