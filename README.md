# Is it too fast?

We replayed real AI coding sessions at faster speed to simulate a possible faster agent. In each one, the assistant does something the user didn't ask for. Can you stop the agent before that?

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

- **Proximity** (quadratic) — how close you got to the mistake before stopping. Stopping early = low score.
- **Speed bonus** (log curve) — based on your effective tok/s. 15 tok/s = 0.59x, 500 = 1.35x, 10k = 2.0x.

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
