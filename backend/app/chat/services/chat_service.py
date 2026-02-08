"""
T036-T042: Chat Service (Phase VI)

[FROM TASKS]: T036-T042 - Chat Service + Chat Endpoint
[FROM SPEC]: speckit.specify §FR1, FR4, FR5

Orchestrates full chat flow with agentic tool loop:
1. Receive user message
2. Validate conversation ownership
3. Append user message
4. Load conversation history
5. Call OpenAI API with tools
6. Execute any tool calls
7. Persist assistant response
8. Return to user

Key Design Principle:
ChatService MUST call ConversationService for persistence.
NO direct database logic allowed in ChatService.

Stateless Design:
- Every request loads full context from DB via ConversationService
- Agent is created fresh per request
- No in-memory conversation buffers
- All state persisted atomically

Agentic Loop:
- Call OpenAI with tools
- Detect tool calls
- Execute via ToolExecutor
- Append tool results (role="tool")
- Re-call OpenAI with results
- Return final assistant message
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI, APIError, Timeout, RateLimitError
import json
import time

from app.chat.models import Message
from app.chat.services.conversation_service import ConversationService
from app.chat.agent.factory import get_agent_factory
from app.chat.agent.error_handler import handle_agent_error
from app.chat.tools.executor import ToolExecutor
from app.chat.tools.registry import validate_tool_name
from app.chat.config import chat_config

logger = logging.getLogger(__name__)


class ChatService:
    """
    Orchestrates chat flow with agentic tool loop.

    Responsibilities:
    - Load conversation history via ConversationService (T025)
    - Invoke OpenAI agent with context
    - Detect and execute tool calls
    - Persist all messages via ConversationService (T026)

    NOT responsible for:
    - Direct database access (use ConversationService)
    - Tool implementation (delegate to ToolExecutor)

    Agentic Loop Implementation:
    1. Call OpenAI API with messages and tools
    2. If no tool_calls → return assistant message
    3. If tool_calls:
       a. Execute each tool via ToolExecutor
       b. Append tool result messages
       c. Re-call OpenAI with tool results
       d. Repeat until no more tool calls or max retries
    4. Return final assistant message

    Flow (per request):
    1. Load conversation history (stateless, fresh from DB) - T025
    2. Append user message to DB - T026
    3. Invoke OpenAI Agent with loaded history - T020, T022
    4. Execute returned tool calls - T029-T032
    5. Store all messages atomically via ConversationService
    6. Return response to caller
    7. Exit with no retained state
    """

    # Configuration constants
    AGENT_TIMEOUT_SECONDS = 4.0
    MAX_TOOL_CALLS_PER_TURN = 5  # Prevent infinite tool loops
    MAX_RETRIES_ON_INVALID_TOOL_CALL = 2
    MAX_CONVERSATION_HISTORY = 50

    @staticmethod
    async def process_chat_message(
        session: AsyncSession,
        conversation_id: UUID,
        user_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process a user message in a conversation with full agentic loop (T036-T042).

        [FROM SPEC]: FR1 - Chat API Endpoint
        [FROM SPEC]: FR4 - Agent Tool Calling
        [FROM SPEC]: FR5 - Multi-Turn Conversations

        Flow:
        1. Validate conversation exists and user owns it
        2. Append user message (T026)
        3. Load recent messages for context (T025)
        4. Invoke agent with OpenAI API (T020)
        5. Handle tool calls if any (T032)
        6. Persist all messages
        7. Return final response

        Args:
            session: AsyncSession for database operations
            conversation_id: UUID of conversation
            user_id: User ID for isolation and logging
            user_message: Message content from user

        Returns:
            {
                "success": bool,
                "conversation_id": str,
                "response": str,
                "tool_calls_executed": List[Dict],
                "message_count": int,
                "execution_time_ms": float
            }

        Raises:
            ValueError: If conversation not found or user doesn't own it
        """
        start_time = time.time()

        try:
            logger.info(
                f"[T036-T042] Processing chat message for user {user_id} "
                f"in conversation {conversation_id}"
            )

            # Step 1: Validate conversation exists and user owns it
            logger.debug(f"[T036] Validating conversation ownership")
            conversation = await ConversationService.get_conversation(
                session, conversation_id, user_id
            )
            if not conversation:
                logger.warning(
                    f"[T036] Conversation {conversation_id} not found for user {user_id}"
                )
                execution_time = (time.time() - start_time) * 1000
                return {
                    "success": False,
                    "error": "conversation_not_found",
                    "response": "I couldn't find that conversation. Please check the ID and try again.",
                    "conversation_id": str(conversation_id),
                    "execution_time_ms": execution_time
                }

            # Step 2: Append user message (T026)
            logger.debug(f"[T036] Appending user message to conversation")
            user_msg_obj = await ConversationService.append_message(
                session,
                conversation_id=conversation_id,
                user_id=user_id,
                role="user",
                content=user_message
            )
            logger.debug(f"[T036] User message persisted: {user_msg_obj.id}")

            # Step 3: Load recent messages for agent context (T025)
            logger.debug(f"[T036] Loading conversation history")
            recent_messages = await ConversationService.get_recent_messages(
                session,
                conversation_id=conversation_id,
                user_id=user_id,
                limit=ChatService.MAX_CONVERSATION_HISTORY
            )
            logger.debug(f"[T036] Loaded {len(recent_messages)} messages for context")

            # Step 4: Prepare agent and invoke with agentic loop
            agent_factory = get_agent_factory()
            agent_config = agent_factory.create_agent(
                user_context={
                    "user_id": user_id,
                    "conversation_id": str(conversation_id),
                    "message_count": len(recent_messages)
                }
            )

            messages_for_agent = ChatService._format_messages_for_agent(recent_messages)

            logger.info(
                f"[T036] Invoking agent with {len(messages_for_agent)} messages, "
                f"{len(agent_config['tools'])} tools available"
            )

            # Step 5: Execute agent with tool loop
            assistant_response, tool_calls_made = await ChatService._invoke_agent_with_tools(
                agent_config=agent_config,
                messages=messages_for_agent,
                user_id=user_id,
                conversation_id=conversation_id,
                session=session
            )

            if not assistant_response or assistant_response.get("success") is False:
                logger.warning(f"[T036] Agent invocation failed")
                execution_time = (time.time() - start_time) * 1000
                return {
                    **assistant_response,
                    "conversation_id": str(conversation_id),
                    "execution_time_ms": execution_time,
                    "tool_calls_executed": []
                }

            final_response = assistant_response.get("response", "")

            # Step 6: Persist assistant response (T026)
            logger.debug(f"[T036] Persisting assistant response to conversation")
            await ConversationService.append_message(
                session,
                conversation_id=conversation_id,
                user_id=user_id,
                role="assistant",
                content=final_response,
                tool_calls=tool_calls_made if tool_calls_made else None
            )
            logger.info(
                f"[T036] Assistant response persisted: {len(final_response)} chars, "
                f"{len(tool_calls_made) if tool_calls_made else 0} tools executed"
            )

            # Step 7: Return response
            execution_time = (time.time() - start_time) * 1000
            logger.info(f"[T036] Chat completed in {execution_time:.0f}ms")

            return {
                "success": True,
                "conversation_id": str(conversation_id),
                "response": final_response,
                "tool_calls_executed": tool_calls_made if tool_calls_made else [],
                "message_count": len(recent_messages) + 2,  # +2 for user and assistant messages
                "execution_time_ms": execution_time
            }

        except Exception as e:
            logger.error(f"[T036] Chat processing failed: {e}", exc_info=True)
            execution_time = (time.time() - start_time) * 1000

            error_response = await handle_agent_error(
                e,
                timeout_seconds=ChatService.AGENT_TIMEOUT_SECONDS,
                context=f"chat:{conversation_id}"
            )

            return {
                "success": False,
                "error": error_response.get("error_type", "unknown"),
                "response": error_response.get("response", "An unexpected error occurred."),
                "conversation_id": str(conversation_id),
                "execution_time_ms": execution_time,
                "tool_calls_executed": []
            }

    @staticmethod
    async def create_conversation(
        session: AsyncSession,
        user_id: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation (T024).

        Delegates entirely to ConversationService (no logic here).

        Args:
            session: AsyncSession
            user_id: User ID
            title: Conversation title (optional)

        Returns:
            {
                "success": bool,
                "conversation_id": str,
                "title": str
            }
        """
        try:
            conversation_id = await ConversationService.create_conversation(
                session,
                user_id=user_id,
                title=title or "New Conversation"
            )
            logger.info(f"[T024] Created conversation {conversation_id} for user {user_id}")
            return {
                "success": True,
                "conversation_id": str(conversation_id),
                "title": title or "New Conversation"
            }
        except Exception as e:
            logger.error(f"[T024] Failed to create conversation: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def list_user_conversations(
        session: AsyncSession,
        user_id: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        List user's conversations ordered by recency (T025).

        Delegates to ConversationService.

        Args:
            session: AsyncSession
            user_id: User ID
            limit: Max conversations to return

        Returns:
            {
                "success": bool,
                "conversations": [...],
                "count": int
            }
        """
        try:
            conversations = await ConversationService.get_user_conversations(
                session,
                user_id=user_id,
                limit=limit
            )
            logger.info(f"[T025] Listed {len(conversations)} conversations for user {user_id}")
            return {
                "success": True,
                "conversations": [
                    {
                        "id": str(conv.id),
                        "title": conv.title,
                        "created_at": conv.created_at.isoformat(),
                        "updated_at": conv.updated_at.isoformat()
                    }
                    for conv in conversations
                ],
                "count": len(conversations)
            }
        except Exception as e:
            logger.error(f"[T025] Failed to list conversations: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "conversations": [],
                "count": 0
            }

    @staticmethod
    async def verify_user_owns_conversation(
        session: AsyncSession,
        conversation_id: UUID,
        user_id: str
    ) -> bool:
        """
        Verify that a user owns a conversation (T045).

        Authorization check to prevent cross-user access.

        Args:
            session: AsyncSession for database operations
            conversation_id: UUID of conversation to check
            user_id: UUID of user claiming ownership

        Returns:
            bool: True if user owns conversation, False otherwise

        Design:
        - Uses ConversationService.get_conversation() which already enforces ownership
        - Returns bool (no exceptions) for clean conditional logic
        - Logs authorization failures
        """
        try:
            # get_conversation already performs ownership check
            # Returns None if conversation not found or user doesn't own it
            conversation = await ConversationService.get_conversation(
                session, conversation_id, user_id
            )

            if conversation:
                logger.debug(f"[T045] Authorization check passed: user {user_id} owns conversation {conversation_id}")
                return True
            else:
                logger.warning(f"[T045] Authorization check failed: user {user_id} does NOT own conversation {conversation_id}")
                return False

        except Exception as e:
            logger.error(f"[T045] Authorization check error: {e}", exc_info=True)
            return False

    @staticmethod
    async def _invoke_agent_with_tools(
        agent_config: Dict[str, Any],
        messages: List[Dict[str, str]],
        user_id: str,
        conversation_id: UUID,
        session: AsyncSession,
        retry_count: int = 0
    ) -> Tuple[Dict[str, Any], Optional[List]]:
        """
        Invoke OpenAI agent with tool support and agentic loop (T036-T042).

        Agentic Loop:
        1. Call OpenAI with messages and tools
        2. If no tool calls → return assistant message
        3. If tool calls:
           a. Execute each tool call
           b. Append tool result messages
           c. Re-call OpenAI with tool results
           d. Repeat until no more tool calls or max retries
        4. Return final assistant message

        Args:
            agent_config: Config dict from AgentFactory (T020)
            messages: Message history in agent format
            user_id: User ID for tool execution
            conversation_id: Conversation ID for logging
            session: AsyncSession for tool execution
            retry_count: Current retry count (internal, starts at 0)

        Returns:
            Tuple of (response_dict, tool_calls_made)
            response_dict: {"success": bool, "response": str, "error"?: str}
            tool_calls_made: List of executed tool calls or None
        """
        try:
            client = agent_config["client"]
            system_prompt = agent_config["system_prompt"]
            tools = agent_config["tools"]

            logger.debug(f"[T036] Agent call #{retry_count + 1}: {len(messages)} messages")

            # Call OpenAI API with timeout
            response = await client.chat.completions.create(
                model=agent_config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                tools=tools,
                tool_choice="auto",
                timeout=ChatService.AGENT_TIMEOUT_SECONDS
            )

            # Extract response
            choice = response.choices[0]
            assistant_message = choice.message.content or ""
            tool_calls = choice.message.tool_calls

            logger.debug(
                f"[T036] Agent response: {len(assistant_message)} chars, "
                f"{len(tool_calls) if tool_calls else 0} tool calls"
            )

            # If no tool calls, return final response
            if not tool_calls:
                logger.info("[T036] Agent completed without tool calls")
                return {
                    "success": True,
                    "response": assistant_message
                }, None

            # Execute tool loop (T029-T032)
            logger.info(f"[T036] Agent requested {len(tool_calls)} tool calls")

            tool_calls_made = []
            executor = ToolExecutor(session)

            # Step 7: Execute each tool call
            for i, tool_call in enumerate(tool_calls):
                if i >= ChatService.MAX_TOOL_CALLS_PER_TURN:
                    logger.warning(
                        f"[T036] Max tool calls per turn ({ChatService.MAX_TOOL_CALLS_PER_TURN}) exceeded"
                    )
                    break

                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments

                logger.debug(f"[T036] Executing tool call {i + 1}: {tool_name}")

                # Validate tool name
                if not validate_tool_name(tool_name):
                    logger.error(f"[T032] Unknown tool: {tool_name}")
                    continue

                # Execute tool
                try:
                    if isinstance(tool_args, str):
                        args_dict = json.loads(tool_args)
                    else:
                        args_dict = tool_args

                    tool_result = await executor.execute(
                        tool_name=tool_name,
                        arguments=args_dict,
                        user_id=user_id,
                        conversation_id=conversation_id
                    )

                    tool_calls_made.append({
                        "id": tool_call.id,
                        "name": tool_name,
                        "arguments": args_dict,
                        "result": tool_result
                    })

                    # Step 8: Append tool result message
                    tool_result_text = (
                        f"Tool '{tool_name}' result: {json.dumps(tool_result.get('result', tool_result))}"
                    )
                    await ConversationService.append_message(
                        session,
                        conversation_id=conversation_id,
                        user_id=user_id,
                        role="tool",
                        content=tool_result_text,
                        tool_calls={"tool_name": tool_name, "result": tool_result.get("result")}
                    )

                    logger.debug(f"[T032] Tool result persisted for {tool_name}")

                except Exception as e:
                    logger.error(f"[T032] Tool execution failed: {e}", exc_info=True)
                    tool_calls_made.append({
                        "id": tool_call.id,
                        "name": tool_name,
                        "error": str(e)
                    })

            # Step 9: Re-call OpenAI with tool results
            logger.info(f"[T036] Re-calling agent with {len(tool_calls_made)} tool results")

            # Prepare updated messages list with tool results
            updated_messages = messages + [
                {
                    "role": "assistant",
                    "content": assistant_message,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in tool_calls
                    ]
                }
            ]

            # Add tool results
            for tool_call in tool_calls_made:
                if "error" not in tool_call:
                    updated_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": str(tool_call["result"].get("result", tool_call["result"]))
                    })
                else:
                    updated_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": f"Error: {tool_call['error']}"
                    })

            # Prevent infinite loops
            if retry_count >= ChatService.MAX_RETRIES_ON_INVALID_TOOL_CALL:
                logger.warning(
                    f"[T036] Max retries ({ChatService.MAX_RETRIES_ON_INVALID_TOOL_CALL}) "
                    "exceeded, returning assistant message"
                )
                return {
                    "success": True,
                    "response": assistant_message
                }, tool_calls_made

            # Recursively re-invoke agent
            return await ChatService._invoke_agent_with_tools(
                agent_config=agent_config,
                messages=updated_messages,
                user_id=user_id,
                conversation_id=conversation_id,
                session=session,
                retry_count=retry_count + 1
            )

        except Timeout:
            logger.warning(f"[T036] Agent timeout after {ChatService.AGENT_TIMEOUT_SECONDS}s")
            return {
                "success": False,
                "error": "timeout",
                "response": f"I'm taking a bit longer than usual. Please try again."
            }, None

        except RateLimitError:
            logger.warning("[T036] OpenAI rate limit reached")
            return {
                "success": False,
                "error": "rate_limit",
                "response": "I've hit a temporary API limit. Please try again in a moment."
            }, None

        except APIError as e:
            logger.error(f"[T036] OpenAI API error: {e}", exc_info=True)
            return {
                "success": False,
                "error": "api_error",
                "response": "I encountered an API error. Please try again."
            }, None

        except Exception as e:
            logger.error(f"[T036] Agent invocation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": "unknown",
                "response": "I encountered an unexpected error. Please try again."
            }, None

    @staticmethod
    def _format_messages_for_agent(conversation_messages: List[Message]) -> List[Dict[str, str]]:
        """
        Convert Message objects from ConversationService to agent-compatible format.

        Args:
            conversation_messages: List of Message objects from database

        Returns:
            List of dicts in agent format: {"role": str, "content": str}
        """
        formatted = []
        for msg in conversation_messages:
            formatted.append({
                "role": msg.role,
                "content": msg.content
            })
        return formatted
