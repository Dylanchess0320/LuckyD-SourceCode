# LuckyD Code

> AI-powered coding agent for Windows — work in your terminal or VS Code.

**Version:** 2.0

## Quick Start

| Step | Command |
|------|---------|
| **Run** | `run.bat` or `python main.py` |
| **One-shot** | `python main.py "refactor this file"` |
| **Help** | `python main.py --help` |

```
run.bat  → interactive REPL
  type /help for commands
  type /model to switch providers
```

## Requirements

- Python 3.10 – 3.12
- Git (for repo-aware features)
- Set `DEEPSEEK_API_KEY` (or your LLM provider key) in `.env`

## Project Layout

```
coding-agent/
├── main.py              ← Entry point
├── ui.py                ← Terminal UI
├── config.py            ← Paths + runtime settings
├── agent.py             ← Core agent logic
├── core/                ← Agent loop, LLM client, providers
├── tools/               ← Tool registry (bash, files, web, git, LSP, memory, …)
├── vscode-extension/    ← VS Code webview extension
├── assets/              ← Static assets (chat.html)
├── data/                ← Runtime data (memory, tasks, workspace, checkpoints)
├── scripts/             ← Helper scripts (auth, build)
├── installers/          ← Python / Git installers
├── docs/                ← Documentation source
├── tests/               ← Test suite
├── .env                 ← Your API keys (create from .env.example)
└── run.bat              ← Windows launcher
```

## Multiple Providers

Configure in `.env` — uncomment **one**:

| Provider | Key | Default Model |
|----------|-----|---------------|
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat |
| OpenAI | `OPENAI_API_KEY` | gpt-4o |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4 |
| Google | `GOOGLE_API_KEY` | gemini-2.0-flash |
| Ollama | *(none)* | codellama |

Swap models at runtime inside the REPL:
```
/model openai gpt-4o
/model anthropic claude-sonnet-4-20250514
```

## License

Proprietary. All rights reserved.




