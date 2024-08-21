
from config import config, register_functions
# from tools_config import config, register_functions


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
        register_functions(llm)

        messages = []
        tools = NotGiven()
        context = OpenAILLMContext(messages, tools)
        context_aggregator = llm.create_context_aggregator(context)
        user_aggregator = context_aggregator.user()
        assistant_aggregator = context_aggregator.assistant()

        rtvi = RTVIProcessor(config=RTVIConfig(config=config))
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

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            logger.debug("FIRST P JOINED")
            video_participant_id = participant["id"]
            transport.capture_participant_transcription(video_participant_id)
            transport.capture_participant_video(video_participant_id, framerate=0)
            logger.debug("SETTING ATTRIBUTE")
            setattr(llm, 'video_participant_id', video_participant_id)

        runner = PipelineRunner()
        await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
