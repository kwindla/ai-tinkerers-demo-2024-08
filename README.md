# A minimum viable code demo for AI Tinkerers

This is a small demo showing how to build an RTVI and Pipecat voice-to-voice AI bot. Small in two senses: I spent about an hour hacking this together, and it's super-simple code that doesn't use a front-end js framework, doesn't have any UI to speak of, and uses a Pipecat pipeline that I just pulled from the `examples/foundational/` directory in the Pipecat repo and lightly customized.

The tech stack is:
  - Deepgram speech-to-text
  - Anthropic LLM
  - Cartesia voice
  - Daily transport

You'll need to open two terminal windows and a web browser.

## js client

In the first terminal ...

```
cd simple-web
npm i
npm start
```

## pipecat bot

```
cd bot
python3.10 -m venv venv
source venv/bin/activate
pip install 'pipecat-ai[daily, anthropic, cartesia, openai, silero]'
pip install python-dotenv
```

## try the demo out

In your `bot` terminal run:

```
python pipeline.py
```

Now open the URL that `npm start` printed out in a web browser. Click "start". In the bot terminal you should see DEBUG log lines printing out, showing the bot reacting to the client joining, and then generating LLM inference and TTS output. The web client should play out the audio.

## tool calling and vision

The default prompt is just a simple "talk like a pirate" message.

To try tool calling and vision, swap `tool_config.py` into `pipeline.py` in place of `config.py`. Then restart the pipeline and rejoin from the web client.

## next steps

This demo is just a single bot, that you manually start, waiting for a connection from a single client. It's easy to deploy this bot to the cloud -- it works exactly the same in the cloud as it does locally. But for an always-on service you'd need to also build a little load-balance/bot-runner back-end.

Here's an example showing a more complete [RTVI service deployment to Modal](https://github.com/rtvi-ai/rtvi-infra-examples/tree/main/02-modal.com)

Daily also offers a "hosted Pipecat/RTVI" service, [Daily Bots](https://www.daily.co/products/daily-bots/), which you are welcome to check out if you're interested in getting up and running with voice agents on infrastructure someone else maintains for you.