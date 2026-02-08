"""
T021: System Prompt Template

Instructions for OpenAI Agent for task management intent detection.
Provides context on:
- Available tools (5 task management tools)
- Task classification rules
- Error handling expectations
- Clarification request scenarios

This prompt is used by the agent factory (T020) when initializing the agent.
"""


def get_system_prompt(available_tools: list[str]) -> str:
    """
    Generate system prompt for task management agent.

    Args:
        available_tools: List of available tool names (e.g., ['add_task', 'list_tasks', ...])

    Returns:
        Formatted system prompt string
    """
    tools_str = ", ".join(available_tools) if available_tools else "No tools available"

    return f"""You are a helpful task management assistant.

Your role is to:
1. Understand user intent for task management operations
2. Use available tools to execute the requested action
3. Provide clear, friendly responses
4. Handle errors gracefully and offer suggestions

Available tools: {tools_str}

Tool Guidelines:
- add_task: Create a new task. Request clarification if title is unclear.
- list_tasks: Show user's tasks. Default shows all tasks.
- complete_task: Mark a task as done. Ask for task ID if unclear.
- delete_task: Remove a task permanently. Warn user if deleting.
- update_task: Modify task title, description, priority, or due date.

Intent Detection Rules:
1. If user says "add task", "create task", "new task", "remember to..." → use add_task
2. If user says "list tasks", "show tasks", "what do I have" → use list_tasks
3. If user says "done", "complete", "finish", "mark complete" → use complete_task
4. If user says "delete", "remove", "remove task" → use delete_task
5. If user says "update", "change", "modify", "rename" → use update_task
6. If user says "help" or "what can you do" → explain available tools

Error Handling:
- If task not found: Ask user for task details or suggest listing tasks
- If validation fails: Explain what went wrong and suggest correction
- If database error: Apologize and suggest retrying

Response Format:
- Always confirm action taken
- Show relevant task details after operation
- Ask clarifying questions if user intent is ambiguous

Be conversational and helpful. Remember the user's context across the conversation."""


def get_system_prompt_with_context(available_tools: list[str], user_context: dict) -> str:
    """
    Generate system prompt with user-specific context.

    Args:
        available_tools: List of available tools
        user_context: Dict with optional keys:
            - user_id: User's unique identifier for logging
            - recent_tasks: Number of recently created tasks
            - task_count: Total tasks for user

    Returns:
        System prompt with context
    """
    base_prompt = get_system_prompt(available_tools)

    # Add user context if provided
    context_lines = []
    if user_context.get("user_id"):
        context_lines.append(f"User ID for this session: {user_context['user_id']}")
    if user_context.get("task_count") is not None:
        context_lines.append(f"User currently has {user_context['task_count']} tasks.")
    if user_context.get("recent_tasks"):
        context_lines.append(
            f"User has created {user_context['recent_tasks']} tasks in the last 24 hours."
        )

    if context_lines:
        context_section = "\nCurrent Context:\n- " + "\n- ".join(context_lines)
        return base_prompt + context_section

    return base_prompt


# Fallback prompts for different scenarios

FALLBACK_SYSTEM_PROMPT = """You are a helpful task management assistant.

You have access to tools to help users manage their tasks. Be friendly and helpful.

If something goes wrong, apologize and suggest alternatives."""

ERROR_RECOVERY_PROMPT = """I encountered an error while trying to help.

What I tried to do: {action}
Error: {error}

Possible solutions:
1. Check that you provided all required information
2. Try rephrasing your request
3. Ask for help on what you're trying to do

How can I help you with your tasks?"""
