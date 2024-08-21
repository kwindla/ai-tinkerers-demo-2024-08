from typing import Any, Dict

from pipecat.frames.frames import LLMMessagesAppendFrame, LLMMessagesUpdateFrame, LLMSetToolsFrame, TTSSpeakFrame
from pipecat.processors.aggregators.llm_response import LLMUserContextAggregator
from pipecat.processors.frameworks.rtvi import (
    ActionResult,
    RTVIAction,
    RTVIActionArgument,
    RTVIProcessor)

from openai._types import NotGiven


async def register_rtvi_actions(rtvi: RTVIProcessor, user_aggregator: LLMUserContextAggregator):
    async def action_llm_run_handler(rtvi: RTVIProcessor, service: str,
                                     arguments: Dict[str, Any]) -> ActionResult:
        interrupt = arguments["interrupt"] if "interrupt" in arguments else True
        if interrupt:
            await rtvi.interrupt_bot()
        frame = user_aggregator.get_context_frame()
        await rtvi.push_frame(frame)
        return True

    async def action_llm_get_context_handler(
            rtvi: RTVIProcessor, service: str, arguments: Dict[str, Any]) -> ActionResult:
        messages = user_aggregator.context.messages
        tools = user_aggregator.context.tools if not isinstance(
            user_aggregator.context.tools, NotGiven) else []
        result = {
            "messages": messages,
            "tools": tools
        }
        return result

    async def action_llm_set_context_handler(
            rtvi: RTVIProcessor, service: str, arguments: Dict[str, Any]) -> ActionResult:
        run_immediately = arguments["run_immediately"] if "run_immediately" in arguments else True

        if run_immediately:
            await rtvi.interrupt_bot()

        # We just interrupted the bot so it should be fine to use the
        # context directly instead of through frame.

        if "messages" in arguments and arguments["messages"]:
            frame = LLMMessagesUpdateFrame(messages=arguments["messages"])
            await rtvi.push_frame(frame)

        if "tools" in arguments and arguments["tools"]:
            frame = LLMSetToolsFrame(tools=arguments["tools"])
            await rtvi.push_frame(frame)

        if run_immediately:
            frame = user_aggregator.get_context_frame()
            await rtvi.push_frame(frame)

        return True

    async def action_llm_append_to_messages_handler(
            rtvi: RTVIProcessor, service: str, arguments: Dict[str, Any]) -> ActionResult:
        run_immediately = arguments["run_immediately"] if "run_immediately" in arguments else True

        if run_immediately:
            await rtvi.interrupt_bot()

        # We just interrupted the bot so it should be find to use the
        # context directly instead of through frame.

        if "messages" in arguments and arguments["messages"]:
            frame = LLMMessagesAppendFrame(messages=arguments["messages"])
            await rtvi.push_frame(frame)

        if run_immediately:
            frame = user_aggregator.get_context_frame()
            await rtvi.push_frame(frame)

        return True

    async def action_tts_say_handler(rtvi: RTVIProcessor, service: str,
                                     arguments: Dict[str, Any]) -> ActionResult:
        await rtvi.interrupt_bot()

        if "text" in arguments:
            frame = TTSSpeakFrame(text=arguments["text"])
            await rtvi.push_frame(frame)

        return True

    async def action_tts_interrupt_handler(
            rtvi: RTVIProcessor, service: str, arguments: Dict[str, Any]) -> ActionResult:
        await rtvi.interrupt_bot()
        return True

    action_llm_run = RTVIAction(
        service="llm",
        action="run",
        result="bool",
        arguments=[RTVIActionArgument(name="interrupt", type="bool")],
        handler=action_llm_run_handler
    )

    action_llm_get_context = RTVIAction(
        service="llm",
        action="get_context",
        result="array",
        handler=action_llm_get_context_handler
    )

    action_llm_set_context = RTVIAction(
        service="llm",
        action="set_context",
        result="bool",
        arguments=[RTVIActionArgument(name="messages", type="array")],
        handler=action_llm_set_context_handler
    )

    action_llm_append_to_messages = RTVIAction(
        service="llm",
        action="append_to_messages",
        result="bool",
        arguments=[
            RTVIActionArgument(name="messages", type="array"),
            RTVIActionArgument(name="run_immediately", type="bool")
        ],
        handler=action_llm_append_to_messages_handler
    )

    action_tts_say = RTVIAction(
        service="tts",
        action="say",
        result="bool",
        arguments=[RTVIActionArgument(name="text", type="string")],
        handler=action_tts_say_handler
    )

    action_tts_interrupt = RTVIAction(
        service="tts",
        action="interrupt",
        result="bool",
        handler=action_tts_interrupt_handler)

    rtvi.register_action(action_llm_run)
    rtvi.register_action(action_llm_get_context)
    rtvi.register_action(action_llm_set_context)
    rtvi.register_action(action_llm_append_to_messages)
    rtvi.register_action(action_tts_say)
    rtvi.register_action(action_tts_interrupt)
