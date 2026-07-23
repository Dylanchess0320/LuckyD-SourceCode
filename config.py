"""
Configuration — paths and provider routing.

Single source of truth:
  config.py         → project paths + runtime settings
  core/providers.py → provider detection / API routing

Backward-compatible aliases (do NOT remove):
  MAX_OUTPUT_CHARS, COMMAND_TIMEOUT_SEC, PROJECT_DIR
"""

from __future__ import annotations

import os
from pathlib import Path

from core.providers import resolve_provider_config

PROJECT_DIR = Path(__file__).parent.resolve()
ENV_FILE = PROJECT_DIR / ".env"

# Runtime data lives under data/ so the repo root stays clean
DATA_DIR = PROJECT_DIR / "data"
MEMORY_DIR = DATA_DIR / "memory_store"
TASKS_DIR = DATA_DIR / "tasks"
WORKSPACE_DIR = DATA_DIR / "workspace"
CHECKPOINTS_DIR = DATA_DIR / "checkpoints"
SKILLS_DIR = PROJECT_DIR / "skills"
ASSETS_DIR = PROJECT_DIR / "assets"

for d in [DATA_DIR, MEMORY_DIR, TASKS_DIR, WORKSPACE_DIR, CHECKPOINTS_DIR, SKILLS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def load_env() -> None:
    """Load .env -- .env values override any stale pre-existing env vars.
    Uses utf-8-sig to safely strip a leading BOM.
    """
    if not ENV_FILE.exists():
        return
    raw = ENV_FILE.read_text(encoding="utf-8-sig")
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        os.environ[key] = val


load_env()

COMMAND_TIMEOUT_SEC = int(os.environ.get("CODING_AGENT_CMD_TIMEOUT", "60"))
MAX_OUTPUT_CHARS_CFG = int(os.environ.get("CODING_AGENT_MAX_OUTPUT", "4000"))


def get_config() -> dict:
    """Get configuration — delegates provider detection to core/providers.py."""
    provider_cfg = resolve_provider_config()

    return {
        **provider_cfg,
        "max_turns": int(os.environ.get("CODING_AGENT_MAX_TURNS", "30")),
        "temperature": float(os.environ.get("CODING_AGENT_TEMP", "0.0")),
        "max_tokens": int(os.environ.get("CODING_AGENT_MAX_TOKENS", "8192")),
        "timeout_sec": int(os.environ.get("CODING_AGENT_TIMEOUT", "120")),
        "max_output_chars": int(os.environ.get("CODING_AGENT_MAX_OUTPUT", "4000")),
        "command_timeout_sec": int(os.environ.get("CODING_AGENT_CMD_TIMEOUT", "60")),
    }


# Backward-compatible aliases
MAX_OUTPUT_CHARS = MAX_OUTPUT_CHARS_CFG
