#
# Copyright (c) 2024, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import aiohttp
import os
import sys

from pipecat.frames.frames import LLMMessagesFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.services.cartesia import CartesiaTTSService

from pipecat.services.anthropic import AnthropicLLMService, AnthropicUserContextAggregator, AnthropicAssistantContextAggregator
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.vad.silero import SileroVADAnalyzer

from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from pipecat.processors.frameworks.rtvi import (
    RTVIConfig,
    RTVIProcessor,
    RTVIServiceConfig,
    RTVIServiceOptionConfig)

from helpers.bot_rtvi_actions import register_rtvi_actions
from helpers.bot_rtvi_services import register_rtvi_services


from openai._types import NotGiven

from loguru import logger

from dotenv import load_dotenv
load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")
# logger.add(sys.stderr, level="TRACE")

video_participant_id = None

# globally declare llm so that we can access it in the get_image function
llm = None


async def get_weather(function_name, tool_call_id, arguments, llm, context, result_callback):
    location = arguments["location"]
    await result_callback(f"The weather in {location} is currently 72 degrees and sunny.")


async def get_image(function_name, tool_call_id, arguments, context, result_callback):
    global llm
    question = arguments["question"]
    await llm.request_image_frame(user_id=video_participant_id, text_content=question)

#
# RTVI default config
#

system_prompt = """\
You are a helpful assistant who converses with a user and answers questions. Respond concisely to general questions.

Your response will be turned into speech so use only simple words and punctuation.

You have access to two tools: get_weather and get_image.

You can respond to questions about the weather using the get_weather tool.

You can answer questions about the user's video stream using the get_image tool. Some examples of phrases that \
indicate you should use the get_image tool are:
  - What do you see?
  - What's in the video?
  - Can you describe the video?
  - Tell me about what you see.
  - Tell me something interesting about what you see.
  - What's happening in the video?

If you need to use a tool, simply use the tool. Do not tell the user the tool you are using. Be brief and concise.
"""


default_config = RTVIConfig(
    config=[
        RTVIServiceConfig(
            service="llm",
            options=[
                RTVIServiceOptionConfig(name="model", value="claude-3-5-sonnet-20240620"),
                RTVIServiceOptionConfig(name="tools", value=[
                    {
                        "name": "get_weather",
                        "description": "Get the current weather in a given location",
                        "input_schema": {"type": "object",
                                         "properties": {"location": {"type": "string",
                                                                     "description": "The city and state, e.g. San Francisco, CA",
                                                                     }},
                                         "required": ["location"],
                                         },
                    },
                    {
                        "name": "get_image",
                        "description": "Get an image from the video stream.",
                        "input_schema": {"type": "object",
                                         "properties": {"question": {"type": "string",
                                                                     "description": "The question that the user is asking about the image.",
                                                                     }},
                                         "required": ["question"],
                                         },
                    }]),
                RTVIServiceOptionConfig(name="initial_messages", value=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": system_prompt,
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": "Start the conversation by introducing yourself."
                    }]),
                RTVIServiceOptionConfig(name="run_on_config", value=True),
            ]),
        RTVIServiceConfig(
            service="tts",
            options=[
                RTVIServiceOptionConfig(
                    name="voice", value="79a125e8-cd45-4c13-8a67-188112f4dd22")  # English Lady
            ])
    ])


async def main():
    global llm

    async with aiohttp.ClientSession() as session:
        room_url = os.getenv("DAILY_SAMPLE_ROOM_URL")
        token = os.getenv("DAILY_ROOM_TOKEN")

        transport = DailyTransport(
            room_url,
            token,
            "Respond bot",
            DailyParams(
                audio_out_enabled=True,
                transcription_enabled=True,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer()
            )
        )

        tts = CartesiaTTSService(
            api_key=os.getenv("CARTESIA_API_KEY"),
            voice_id="79a125e8-cd45-4c13-8a67-188112f4dd22",  # British Lady
            sample_rate=16000,
        )

        llm = AnthropicLLMService(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-5-sonnet-20240620",
            enable_prompt_caching_beta=True
        )
        # llm.register_function("get_weather", get_weather)
        # llm.register_function("get_image", get_image)

        # context = OpenAILLMContext(messages, tools)
        # context_aggregator = llm.create_context_aggregator(context)

        messages = []
        tools = NotGiven()
        context = OpenAILLMContext(messages, tools)
        context_aggregator = llm.create_context_aggregator(context)
        user_aggregator = context_aggregator.user()
        assistant_aggregator = context_aggregator.assistant()

        rtvi = RTVIProcessor(config=default_config)
        await register_rtvi_services(rtvi, user_aggregator)
        await register_rtvi_actions(rtvi, user_aggregator)

        llm.register_function(
            None,
            rtvi.handle_function_call,
            start_callback=rtvi.handle_function_call_start)

        pipeline = Pipeline([
            transport.input(),               # Transport user input
            rtvi,                            # RTVI
            context_aggregator.user(),       # User speech to text
            llm,                             # LLM
            tts,                             # TTS
            transport.output(),              # Transport bot output
            context_aggregator.assistant(),  # Assistant spoken responses and tool context
        ])

        task = PipelineTask(
            pipeline,
            PipelineParams(
                allow_interruptions=True,
                enable_metrics=True))

        @ transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            global video_participant_id
            video_participant_id = participant["id"]
            transport.capture_participant_transcription(video_participant_id)
            transport.capture_participant_video(video_participant_id, framerate=0)
            # Kick off the conversation.
            # await task.queue_frames([context_aggregator.user().get_context_frame()])

        runner = PipelineRunner()
        await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
