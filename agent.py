"""
CodingAgent — backward-compatibility shim.

The canonical implementation now lives in core/agent_loop.py (modular architecture
using core/llm_client.py, core/message_builder.py, core/context_manager.py,
core/hooks.py, and core/checkpoint.py). This module re-exports it so that
existing imports (from agent import CodingAgent) continue to work.
"""
from __future__ import annotations

import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import PROJECT_DIR  # noqa: E402

# Auto-register built-in tools (populates the tool registry)
import tools.file_tools       # noqa: F401
import tools.bash_tool        # noqa: F401
import tools.git_tools        # noqa: F401
import tools.web_tools        # noqa: F401
import tools.browser_tools    # noqa: F401
import tools.memory_tools     # noqa: F401
import tools.subagent_tool    # noqa: F401
import tools.skill_tools      # noqa: F401
import tools.graphify_tool    # noqa: F401
import tools.agent_orchestration  # noqa: F401
import tools.data_tools           # noqa: F401
import tools.lsp_tools            # noqa: F401
import tools.task_tools           # noqa: F401
import tools.utility_tools        # noqa: F401
import tools.session_tools        # noqa: F401
import tools.config_tool          # noqa: F401
import tools.brief_tool           # noqa: F401
import tools.ask_question_tool    # noqa: F401
import tools.plan_tools           # noqa: F401
import tools.datetime_tools       # noqa: F401

from project import ProjectDetector  # noqa: E402

_project_info = None
try:
    _detector = ProjectDetector()
    _project_info = _detector.detect(PROJECT_DIR)
except Exception:
    pass

from core.agent_loop import CodingAgent  # noqa: E402,F401

SYSTEM_PROMPT = """You are LuckyD Code, an AI coding assistant in a terminal.

Answer concisely. For code: use Bash/Read/Write/Edit/Glob/Grep tools.
For questions: answer directly.
"""
