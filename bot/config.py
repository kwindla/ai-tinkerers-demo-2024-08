from loguru import logger


system_prompt = """\
You are a helpful assistant. You always talk like a pirate!
"""

config = [{"service": "tts",
           "options": [{"name": "voice",
                        "value": "79a125e8-cd45-4c13-8a67-188112f4dd22"}]},
          {"service": "llm",
           "options": [{"name": "model",
                        "value": "claude-3-5-sonnet-20240620"},
                       {"name": "initial_messages",
                        "value": [{"role": "system",
                                   "content": [{"type": "text",
                                                "text": system_prompt,
                                                }]},
                                  {"role": "user",
                                   "content": "Start the conversation by introducing yourself."}]},
                       {"name": "run_on_config",
                        "value": True}]}]


def register_functions(llm):
    pass
