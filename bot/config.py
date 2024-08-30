from loguru import logger


system_prompt = """\
You are a helpful assistant. You always talk like a pirate!
"""

config = [{"service": "tts",
           "options": [{"name": "voice",
                        "value": "79a125e8-cd45-4c13-8a67-188112f4dd22"}]},
          {"service": "llm",
           "options": [{"name": "model",
                        "value": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"},
                       {"name": "initial_messages",
                        "value": []},
                       {"name": "run_on_config",
                        "value": False}]}]


async def get_current_weather(
        function_name,
        tool_call_id,
        arguments,
        llm,
        context,
        result_callback):
    location = arguments["location"]
    logger.debug("Getting weather for {location}")
    await result_callback({"location": location, "conditions": "currently 72 degrees and sunny."})


async def get_image(function_name, tool_call_id, arguments, llm, context, result_callback):
    question = arguments["question"]
    video_participant_id = getattr(llm, 'video_participant_id', None)
    logger.debug(f"VIDEO PARTICIPANT ID: {video_participant_id}")
    await llm.request_image_frame(user_id=video_participant_id, text_content=question)
    # don't return anything, because our Together/Moondream adapter will
    # append a tool response message


def register_functions(llm):
    llm.register_function("get_current_weather", get_current_weather)
    llm.register_function("get_image", get_image)
