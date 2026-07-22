# Installation

## Prerequisites

- **Python 3.10 or higher** — [Download Python](https://www.python.org/downloads/)
- **Git** — [Download Git](https://git-scm.com/downloads)
- **An API key** for your chosen LLM provider

## Standard Installation

### Install from PyPI

```bash
pip install luckyd-code
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/luckyd/coding-agent.git
cd coding-agent

# Create and activate a virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Install with Development Tools

```bash
pip install -r requirements-dev.txt
```

## Docker Installation

```bash
# Build the Docker image
docker build -t luckyd-code .

# Or with Docker Compose
docker compose build
```

## VS Code Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "LuckyD Code" or install from `.vsix`
4. Reload VS Code
5. Open command palette (Ctrl+Shift+P) and run `LuckyD Code: Open Agent Chat`

## Verification

Verify your installation:

```bash
python main.py --help
```

You should see the help message with available options.
