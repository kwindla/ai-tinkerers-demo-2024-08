import json

from loguru import logger

weatherTool = {
    "name": "get_current_weather",
    "description": "Get the current weather in a given location",
    "parameters": {
        "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
            },
        "required": ["location"],
    },
}

getImageTool = {
    "name": "get_image",
    "description": "Get an image from the video stream.",
    "parameters": {
        "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question that the user is asking about the image.",
                },
            },
        "required": ["question"],
    },
}


system_prompt = f"""\
You are a helpful AI assistant. You are built on the Llama 3.1 405 billion parameter model.

You have access to the following functions:

Use the function '{weatherTool["name"]}' to '{weatherTool["description"]}':
{json.dumps(weatherTool)}

Use the function '{getImageTool["name"]}' to '{getImageTool["description"]}':
{json.dumps(getImageTool)}

If you choose to call a function ONLY reply in the following format with no prefix or suffix:

<function=example_function_name>{{\"example_name\": \"example_value\"}}</function>

Reminder:
- Function calls MUST follow the specified format, start with <function= and end with </function>
- Required parameters MUST be specified
- Only call one function at a time
- Put the entire function call reply on one line
- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls

"""

test_case_bad_function_call = [{"role": "system", "content": "You are a helpful AI assistant. You are built on the Llama 3.1 405 billion parameter model.\n\nYou have access to the following functions:\n\nUse the function 'get_current_weather' to 'Get the current weather in a given location':\n{\"name\": \"get_current_weather\", \"description\": \"Get the current weather in a given location\", \"parameters\": {\"type\": \"object\", \"properties\": {\"location\": {\"type\": \"string\", \"description\": \"The city and state, e.g. San Francisco, CA\"}}, \"required\": [\"location\"]}}\n\nUse the function 'get_image' to 'Get an image from the video stream.':\n{\"name\": \"get_image\", \"description\": \"Get an image from the video stream.\", \"parameters\": {\"type\": \"object\", \"properties\": {\"question\": {\"type\": \"string\", \"description\": \"The question that the user is asking about the image.\"}}, \"required\": [\"question\"]}}\n\nIf you choose to call a function ONLY reply in the following format with no prefix or suffix:\n\n<function=example_function_name>{\"example_name\": \"example_value\"}</function>\n\nReminder:\n- Function calls MUST follow the specified format, start with <function= and end with </function>\n- Required parameters MUST be specified\n- Only call one function at a time\n- Put the entire function call reply on one line\n- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls\n\n"}, {"role": "user", "content": "Start the conversation by introducing yourself."}, {"role": "assistant", "content": " Hello! I'm an AI"}, {"role": "user", "content": " I'm still working in San Francisco right now."}]

config = [{"service": "tts",
           "options": [{"name": "voice",
                        "value": "79a125e8-cd45-4c13-8a67-188112f4dd22"}]},
          {"service": "llm",
           "options": [{"name": "model",
                        "value": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"},
                       {"name": "initial_messages",
                        "value": [{"role": "system",
                                   "content": system_prompt,
                                   },
                                  {"role": "user",
                                   "content": "Start the conversation by introducing yourself."}]},
                       #  "value": test_case_bad_function_call},
                       {"name": "run_on_config",
                        "value": True}]}]


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
