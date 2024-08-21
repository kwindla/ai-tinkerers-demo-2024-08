from pipecat.frames.frames import (
    ErrorFrame,
    LLMEnablePromptCachingFrame,
    LLMMessagesUpdateFrame,
    LLMModelUpdateFrame,
    LLMSetToolsFrame,
    TTSVoiceUpdateFrame,
    VADParamsUpdateFrame)
from pipecat.processors.aggregators.llm_response import LLMUserContextAggregator
from pipecat.processors.frame_processor import FrameDirection
from pipecat.processors.frameworks.rtvi import (
    RTVIProcessor,
    RTVIService,
    RTVIServiceOption,
    RTVIServiceOptionConfig)
from pipecat.vad.vad_analyzer import VADParams


async def register_rtvi_services(rtvi: RTVIProcessor, user_aggregator: LLMUserContextAggregator):
    async def config_llm_model_handler(
            rtvi: RTVIProcessor,
            service: str,
            option: RTVIServiceOptionConfig):
        frame = LLMModelUpdateFrame(option.value)
        await rtvi.push_frame(frame)

    async def config_llm_messages_handler(
            rtvi: RTVIProcessor,
            service: str,
            option: RTVIServiceOptionConfig):
        if option.value:
            frame = LLMMessagesUpdateFrame(option.value)
            await rtvi.push_frame(frame)

    async def config_llm_enable_prompt_caching_handler(
            rtvi: RTVIProcessor,
            service: str,
            option: RTVIServiceOptionConfig):
        frame = LLMEnablePromptCachingFrame(enable=option.value)
        await rtvi.push_frame(frame)

    async def config_llm_run_on_config_handler(
            rtvi: RTVIProcessor,
            service: str,
            option: RTVIServiceOptionConfig):
        if option.value:
            # Run inference with the updated messages. Make sure to send the
            # frame from the RTVI to keep ordering.
            frame = user_aggregator.get_context_frame()
            await rtvi.push_frame(frame)

    async def config_tts_voice_handler(
            rtvi: RTVIProcessor,
            service: str,
            option: RTVIServiceOptionConfig):
        frame = TTSVoiceUpdateFrame(option.value)
        await rtvi.push_frame(frame)

    async def config_tools_handler(
            rtvi: RTVIProcessor,
            service: str,
            option: RTVIServiceOptionConfig):
        frame = LLMSetToolsFrame(option.value)
        await rtvi.push_frame(frame)

    async def config_vad_params_handler(
            rtvi: RTVIProcessor,
            service: str,
            option: RTVIServiceOptionConfig):
        try:
            extra_fields = set(option.value.keys()) - set(VADParams.model_fields.keys())
            if extra_fields:
                raise ValueError(f"Extra fields found in VAD params: {extra_fields}")
            vad_params = VADParams.model_validate(option.value, strict=True)
        except Exception as e:
            await rtvi.push_error(ErrorFrame(f"Error setting VAD params: {e}"))
            return
        frame = VADParamsUpdateFrame(vad_params)
        await rtvi.push_frame(frame, FrameDirection.UPSTREAM)

    rtvi_vad = RTVIService(
        name="vad",
        options=[
            RTVIServiceOption(
                name="params",
                type="object",
                handler=config_vad_params_handler),
        ]
    )

    rtvi_llm = RTVIService(
        name="llm",
        options=[
            RTVIServiceOption(
                name="model",
                type="string",
                handler=config_llm_model_handler),
            RTVIServiceOption(
                name="initial_messages",
                type="array",
                handler=config_llm_messages_handler),
            RTVIServiceOption(
                name="enable_prompt_caching",
                type="bool",
                handler=config_llm_enable_prompt_caching_handler),
            RTVIServiceOption(
                name="run_on_config",
                type="bool",
                handler=config_llm_run_on_config_handler),
            RTVIServiceOption(
                name="tools",
                type="array",
                handler=config_tools_handler)
        ])

    rtvi_tts = RTVIService(
        name="tts",
        options=[
            RTVIServiceOption(
                name="voice",
                type="string",
                handler=config_tts_voice_handler),
        ])

    rtvi.register_service(rtvi_vad)
    rtvi.register_service(rtvi_llm)
    rtvi.register_service(rtvi_tts)
