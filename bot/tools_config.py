from loguru import logger


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

config = [{"service": "tts",
           "options": [{"name": "voice",
                        "value": "79a125e8-cd45-4c13-8a67-188112f4dd22"}]},
          {"service": "llm",
           "options": [{"name": "model",
                        "value": "claude-3-5-sonnet-20240620"},
                       {"name": "tools",
                        "value": [{"name": "get_weather",
                                   "description": "Get the current weather in a given location",
                                   "input_schema": {"type": "object",
                                                    "properties": {"location": {"type": "string",
                                                                                "description": "The city and state, e.g. San Francisco, CA",
                                                                                }},
                                                    "required": ["location"],
                                                    },
                                   },
                                  {"name": "get_image",
                                   "description": "Get an image from the video stream.",
                                   "input_schema": {"type": "object",
                                                    "properties": {"question": {"type": "string",
                                                                                "description": "The question that the user is asking about the image.",
                                                                                }},
                                                    "required": ["question"],
                                                    },
                                   }]},
                       {"name": "initial_messages",
                        "value": [{"role": "system",
                                   "content": [{"type": "text",
                                                "text": system_prompt,
                                                }]},
                                  {"role": "user",
                                   "content": "Start the conversation by introducing yourself."}]},
                       {"name": "run_on_config",
                        "value": True}]}]


async def get_weather(function_name, tool_call_id, arguments, llm, context, result_callback):
    location = arguments["location"]
    await result_callback(f"The weather in {location} is currently 72 degrees and sunny.")


async def get_image(function_name, tool_call_id, arguments, llm, context, result_callback):
    question = arguments["question"]
    video_participant_id = getattr(llm, 'video_participant_id', None)
    logger.debug(f"VIDEO PARTICIPANT ID: {video_participant_id}")
    await llm.request_image_frame(user_id=video_participant_id, text_content=question)
    await result_callback("done.")


def register_functions(llm):
    llm.register_function("get_weather", get_weather)
    llm.register_function("get_image", get_image)
