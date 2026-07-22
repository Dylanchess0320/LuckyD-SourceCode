"""
Tool approval hook — requests user permission before executing dangerous tools.
Borrows pattern from Cline's tool-approval.ts with file-based IPC mechanism.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from core.hooks import AgentPlugin, HookContext
from core.types import ToolPermissionLevel, ToolApprovalRequest, ToolApprovalResult


_TOOL_PERMISSIONS: dict[str, ToolPermissionLevel] = {
    "Read": ToolPermissionLevel.ALWAYS_ALLOW,
    "Glob": ToolPermissionLevel.ALWAYS_ALLOW,
    "Grep": ToolPermissionLevel.ALWAYS_ALLOW,
    "WebSearch": ToolPermissionLevel.ALWAYS_ALLOW,
    "WebFetch": ToolPermissionLevel.ALWAYS_ALLOW,
    "ShellHistory": ToolPermissionLevel.ALWAYS_ALLOW,
    "TodoRead": ToolPermissionLevel.ALWAYS_ALLOW,
    "Datetime": ToolPermissionLevel.ALWAYS_ALLOW,
    "Edit": ToolPermissionLevel.NORMAL,
    "Write": ToolPermissionLevel.REQUIRES_APPROVAL,
    "Bash": ToolPermissionLevel.REQUIRES_APPROVAL,
    "SubAgent": ToolPermissionLevel.NORMAL,
    "TodoWrite": ToolPermissionLevel.NORMAL,
    "AgentHandoff": ToolPermissionLevel.NORMAL,
    "MemoryAdd": ToolPermissionLevel.NORMAL,
    "MemorySearch": ToolPermissionLevel.ALWAYS_ALLOW,
    "BrowserNavigate": ToolPermissionLevel.REQUIRES_APPROVAL,
    "BrowserClick": ToolPermissionLevel.REQUIRES_APPROVAL,
    "GitCommit": ToolPermissionLevel.REQUIRES_APPROVAL,
    "GitPush": ToolPermissionLevel.REQUIRES_APPROVAL,
    "Graphify": ToolPermissionLevel.REQUIRES_APPROVAL,
}


class ApprovalHook(AgentPlugin):
    """Hook that requests user approval before executing dangerous tools."""
    name = "approval"

    def __init__(
        self,
        approval_callback: Callable[[ToolApprovalRequest], ToolApprovalResult] | None = None,
        approval_dir: str | None = None,
        session_id: str = "default",
        timeout_ms: int = 300000,
    ):
        self.approval_callback = approval_callback
        self.approval_dir = approval_dir
        self.session_id = session_id
        self.timeout_ms = timeout_ms
        self.auto_approve_all = False

    def set_permission(self, tool_name: str, level: ToolPermissionLevel):
        _TOOL_PERMISSIONS[tool_name] = level

    def get_permission(self, tool_name: str) -> ToolPermissionLevel:
        return _TOOL_PERMISSIONS.get(tool_name, ToolPermissionLevel.NORMAL)

    def before_tool(self, tool_name: str, tool_args: dict, ctx: HookContext) -> None | dict:
        level = self.get_permission(tool_name)
        if level == ToolPermissionLevel.BLOCKED:
            return {"role": "tool", "tool_call_id": tool_args.get("_id", "unknown"),
                    "content": f"Error: Tool '{tool_name}' is blocked for security reasons."}
        if level == ToolPermissionLevel.ALWAYS_ALLOW or self.auto_approve_all:
            return None
        if level == ToolPermissionLevel.REQUIRES_APPROVAL:
            return self._request_approval(tool_name, tool_args)
        # NORMAL: check policy
        if ctx.config:
            policies = ctx.config.get("tool_policies", {})
            tp = policies.get(tool_name, policies.get("*", {}))
            if tp.get("auto_approve", False):
                return None
            if tp.get("block", False):
                return {"role": "tool", "tool_call_id": tool_args.get("_id", "unknown"),
                        "content": f"Error: Tool '{tool_name}' is blocked by policy."}
        return self._request_approval(tool_name, tool_args)

    def _request_approval(self, tool_name: str, tool_args: dict) -> dict | None:
        clean_args = {k: v for k, v in tool_args.items() if not k.startswith("_")}
        request = ToolApprovalRequest(
            tool_name=tool_name, tool_args=clean_args,
            call_id=tool_args.get("_id", "unknown"),
            session_id=self.session_id, turn=0,
        )
        if self.approval_callback:
            result = self.approval_callback(request)
            if not result or not result.approved:
                reason = result.reason if result else "No approval provided"
                return {"role": "tool", "tool_call_id": request.call_id,
                        "content": f"Tool execution denied by user: {reason}"}
            return None
        if self.approval_dir:
            return self._file_based_approval(request)
        return {"role": "tool", "tool_call_id": request.call_id,
                "content": f"Error: Tool '{tool_name}' requires approval but no approval mechanism configured."}

    def _file_based_approval(self, request: ToolApprovalRequest) -> dict | None:
        """File-based IPC approval (pattern from Cline's tool-approval.ts)."""
        approval_dir = Path(self.approval_dir)
        approval_dir.mkdir(parents=True, exist_ok=True)
        rid = request.tool_name.replace(" ", "_").lower()
        req_path = approval_dir / f"{self.session_id}.request.{rid}.json"
        dec_path = approval_dir / f"{self.session_id}.decision.{rid}.json"
        req_path.write_text(json.dumps({
            "requestId": rid, "sessionId": self.session_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "toolCallId": request.call_id, "toolName": request.tool_name,
            "input": request.tool_args, "risk": "high",
        }, indent=2))
        started_at = time.monotonic()
        while (time.monotonic() - started_at) * 1000 < self.timeout_ms:
            if dec_path.exists():
                try:
                    data = json.loads(dec_path.read_text())
                    dec_path.unlink(missing_ok=True)
                    req_path.unlink(missing_ok=True)
                    if data.get("approved", False):
                        return None
                    return {"role": "tool", "tool_call_id": request.call_id,
                            "content": f"Tool execution denied: {data.get('reason', 'No reason')}"}
                except Exception:
                    pass
            time.sleep(0.2)
        req_path.unlink(missing_ok=True)
        return {"role": "tool", "tool_call_id": request.call_id,
                "content": f"Tool approval timed out after {self.timeout_ms/1000}s for '{request.tool_name}'."}

