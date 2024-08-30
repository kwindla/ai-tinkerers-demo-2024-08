const weatherTool = {
  name: "get_current_weather",
  description: "Get the current weather in a given location",
  parameters: {
      type: "object",
      properties: {
          location: {
              type: "string",
              description: "The city and state, e.g. San Francisco, CA",
          },
      },
      required: ["location"],
  },
};

const getImageTool = {
  name: "get_image",
  description: "Get an image from the video stream.",
  parameters: {
      type: "object",
      properties: {
          question: {
              type: "string",
              description: "The question that the user is asking about the image.",
          },
      },
      required: ["question"],
  },
};

const systemPrompt = `\
You are a helpful AI assistant. You are built on the Llama 3.1 405 billion parameter model.

You have access to the following functions:

Use the function '${weatherTool.name}' to '${weatherTool.description}':
${JSON.stringify(weatherTool)}

Use the function '${getImageTool.name}' to '${getImageTool.description}':
${JSON.stringify(getImageTool)}

If you choose to call a function ONLY reply in the following format with no prefix or suffix:

<function=example_function_name>{"example_name": "example_value"}</function>

Reminder:
- Function calls MUST follow the specified format, start with <function= and end with </function>
- Required parameters MUST be specified
- Only call one function at a time
- Put the entire function call reply on one line
- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls

`;

export const visionConfig = [
  { service: "llm",
    options: [
      {
        name: "model",
        value: "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
      },
      {
        name: "initial_messages",
        value: [
          {
            role: "system",
            content:  systemPrompt
          },
        ]
      },
    ]
  }
];