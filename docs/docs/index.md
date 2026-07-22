# LuckyD Code 🚀

**AI-powered coding agent for the terminal and VS Code.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)
![Status](https://img.shields.io/badge/Status-Active-green)

---

## ✨ Features

- **Multi-LLM** — DeepSeek, OpenAI, Anthropic, Google, Ollama
- **20+ Tools** — file ops, bash, git, web, browser, LSP, sub-agents
- **Memory Graph** — persistent knowledge with BM25 + ONNX embeddings
- **VS Code Extension** — built-in chat panel
- **Streaming UI** — Rich terminal with real-time token display
- **Safe Execution** — command sandboxing with blocklist
- **Cost Tracking** — per-session token and cost monitoring
- **Project Intelligence** — auto-detects project type and framework

## 🚀 Quick Start

```bash
# Install
pip install luckyd-code

# Run interactive REPL
luckyd-code

# One-shot query
luckyd-code "explain this codebase"

# With specific model
luckyd-code --model pro --thinking
```

## 📦 Installation

### Requirements

- Python 3.10+
- Git
- API key for your chosen LLM provider

### From Source

```bash
git clone https://github.com/luckyd/coding-agent.git
cd coding-agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and set your API key:

```bash
cp .env.example .env
```

Then edit `.env` with your preferred provider.

## 🎮 Usage

### Interactive REPL

```bash
python main.py
```

### One-Shot Mode

```bash
python main.py "generate tests for this project"
```

### With Model Selection

```bash
python main.py --model pro --thinking
python main.py --model openai gpt-4o
```

### Docker

```bash
docker compose build
docker compose run app
```

## 📚 Documentation

Full documentation is available at [luckyd.github.io/coding-agent](https://luckyd.github.io/coding-agent/).

## 🤝 Contributing

See [CONTRIBUTING.md](https://github.com/luckyd/coding-agent/blob/main/CONTRIBUTING.md).

## 📄 License

Proprietary. All rights reserved.
