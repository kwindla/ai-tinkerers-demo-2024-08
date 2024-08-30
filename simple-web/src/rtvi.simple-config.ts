
export const simpleConfig = [
  { service: "llm",
    options: [
      {
        name: "model",
        value: "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
      },
      {
        name: "initial_messages",
        value: [
          {
            role: "system",
            content:  "You are a helpful assistant. You always talk like a pirate!"
          },
          {
            role: "user",
            content: "Say 'hello'."
          }
        ]
      },
    ]
  }
];