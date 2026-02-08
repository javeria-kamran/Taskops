"""
T022: Tool Processor

Converts MCP tool outputs to agent-compatible format.
Handles tool chaining and result preparation for agent context.

Responsibilities:
1. Format tool results for agent consumption
2. Handle tool chaining (sequential tool calls)
3. Track tool execution history
4. Convert errors to agent-friendly format
"""

import logging
from typing import Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolExecutionResult:
    """
    Represents a tool execution result.

    Attributes:
        tool_name: Name of executed tool
        success: Whether execution succeeded
        result: Tool output (if success)
        error: Error message (if failure)
        execution_time_ms: Time spent executing tool
        timestamp: When tool was executed
    """

    def __init__(
        self,
        tool_name: str,
        success: bool,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        execution_time_ms: float = 0.0
    ):
        self.tool_name = tool_name
        self.success = success
        self.result = result
        self.error = error
        self.execution_time_ms = execution_time_ms
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging or serialization."""
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "result": self.result if self.success else None,
            "error": self.error if not self.success else None,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat()
        }

    def to_agent_format(self) -> dict[str, Any]:
        """
        Convert to format suitable for OpenAI agent consumption.

        Format for agent:
        {
            "role": "tool",
            "tool_use_id": "<id>",
            "content": "Tool output or error message"
        }
        """
        if self.success:
            # Format successful result
            result_text = self._format_result(self.result)
            return {
                "role": "tool",
                "tool_name": self.tool_name,
                "content": result_text
            }
        else:
            # Format error
            return {
                "role": "tool",
                "tool_name": self.tool_name,
                "error": True,
                "content": self.error or "Unknown error"
            }

    def _format_result(self, result: Any) -> str:
        """
        Format tool result as human-readable string for agent.

        Args:
            result: Tool result dict/list/etc.

        Returns:
            Formatted string
        """
        if isinstance(result, dict):
            # Format dict results
            if result.get("tasks"):  # list_tasks result
                task_strs = []
                for task in result["tasks"]:
                    task_str = f"- {task.get('title', 'Untitled')} ({task.get('status', 'unknown')})"
                    task_strs.append(task_str)
                return f"Found {result['count']} tasks:\n" + "\n".join(task_strs)

            # Generic dict formatting
            lines = []
            for key, value in result.items():
                if key != "result":  # Skip 'result' wrapper key
                    lines.append(f"{key}: {value}")
            return "\n".join(lines) if lines else str(result)

        elif isinstance(result, list):
            # Format list results
            return "\n".join(str(item) for item in result)

        else:
            # Format primitive results
            return str(result)


class ToolProcessor:
    """Processes tool execution results for agent consumption."""

    def __init__(self):
        """Initialize tool processor."""
        self.execution_history: list[ToolExecutionResult] = []
        self.max_history = 100  # Keep last 100 tool executions

    def record_execution(self, result: ToolExecutionResult) -> None:
        """
        Record a tool execution result.

        Args:
            result: ToolExecutionResult to record
        """
        self.execution_history.append(result)

        # Trim history if too long
        if len(self.execution_history) > self.max_history:
            self.execution_history = self.execution_history[-self.max_history:]

        logger.info(f"Tool execution recorded: {result.tool_name} ({result.execution_time_ms:.0f}ms)")

    def format_for_agent(self, result: ToolExecutionResult) -> dict[str, Any]:
        """
        Format tool result for agent consumption.

        Args:
            result: ToolExecutionResult

        Returns:
            Agent-compatible format dict
        """
        return result.to_agent_format()

    def format_tool_calls_for_messages(self, results: list[ToolExecutionResult]) -> list[dict[str, Any]]:
        """
        Format multiple tool results for conversation messages.

        Args:
            results: List of ToolExecutionResult

        Returns:
            List of formatted results for agent context
        """
        return [self.format_for_agent(result) for result in results]

    def get_execution_history_summary(self, limit: int = 10) -> str:
        """
        Get human-readable summary of recent tool executions.

        Args:
            limit: Number of recent executions to include

        Returns:
            Formatted summary string
        """
        recent = self.execution_history[-limit:]
        if not recent:
            return "No tool executions yet."

        lines = ["Recent tool executions:"]
        for result in recent:
            status = "✓" if result.success else "✗"
            lines.append(
                f"  {status} {result.tool_name} ({result.execution_time_ms:.0f}ms) - "
                f"{datetime.fromisoformat(result.timestamp.isoformat()).strftime('%H:%M:%S')}"
            )
        return "\n".join(lines)

    async def handle_tool_chaining(
        self,
        tool_sequence: list[dict[str, Any]],
        execute_fn,
        user_id: str,
        session: Any
    ) -> list[ToolExecutionResult]:
        """
        Execute a sequence of tools (tool chaining).

        Args:
            tool_sequence: List of {tool_name: str, input: dict}
            execute_fn: Async function to execute tool
            user_id: User ID for isolation
            session: Database session

        Returns:
            List of ToolExecutionResult for each tool
        """
        results = []

        for tool_call in tool_sequence:
            tool_name = tool_call.get("tool_name")
            tool_input = tool_call.get("input", {})

            try:
                import time
                start_time = time.time()

                result = await execute_fn(tool_name, tool_input, user_id, session)

                execution_time_ms = (time.time() - start_time) * 1000
                tool_result = ToolExecutionResult(
                    tool_name=tool_name,
                    success=True,
                    result=result.get("result") if isinstance(result, dict) else result,
                    execution_time_ms=execution_time_ms
                )

            except Exception as e:
                tool_result = ToolExecutionResult(
                    tool_name=tool_name,
                    success=False,
                    error=str(e),
                    execution_time_ms=0.0
                )

            results.append(tool_result)
            self.record_execution(tool_result)

            logger.info(f"Tool execution: {tool_name} - {'Success' if tool_result.success else 'Failed'}")

        return results


# Global tool processor instance
_tool_processor: Optional[ToolProcessor] = None


def initialize_tool_processor() -> ToolProcessor:
    """
    Initialize global tool processor.

    Returns:
        Initialized ToolProcessor
    """
    global _tool_processor
    _tool_processor = ToolProcessor()
    return _tool_processor


def get_tool_processor() -> ToolProcessor:
    """
    Get global tool processor instance.

    Returns:
        ToolProcessor

    Raises:
        RuntimeError: If not initialized
    """
    if not _tool_processor:
        raise RuntimeError("Tool processor not initialized")
    return _tool_processor
