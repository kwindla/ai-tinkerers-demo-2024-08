
import { DailyVoiceClient } from "realtime-ai-daily";
import { LLMHelper } from "realtime-ai";


function main() {
  const voiceClient = new DailyVoiceClient({
    // connection setup for local demo
    customAuthHandler: async () => {
      return {
        room_url: 'https://kwindla.daily.co/adaptive',
        token: ''
      }
    },

    //
    // client setup
    //
    enableMic: true,
    // enableCam: true,
    callbacks:{
      onBotReady: botReadyHandler,
      onTrackStarted: trackStartedHandler
    },

    //
    // the services the bot we are talking to supports
    //
    services: {
       llm: "anthropic",
       tts: "cartesia",
     }
  });
  const llmHelper = new LLMHelper({
    callbacks: {
      onLLMFunctionCall: (fn) => {
        console.log("LLM function call", fn);
      },
    },
  });
  voiceClient.registerHelper("llm", llmHelper);
  voiceClient.start()
}

function botReadyHandler() {
  console.log('Bot ready');
  const header = document.getElementById('main-header');
  header.textContent = 'Connected ...';
}

function trackStartedHandler(track, participant) {
  const app = document.getElementById('app');

  console.log('Track started', track, participant);

  if (participant.local && track.kind == 'video') {
    console.log('local video track started', track, participant);
    let videoElement = document.createElement('video');
    videoElement.srcObject = new MediaStream([track]);
    app.appendChild(videoElement);
    videoElement.play();
    return;
  }

  if (!participant.local && track.kind == 'audio') {
    console.log('audio track started', track, participant);
    let audioElement = document.createElement('audio');
    audioElement.srcObject = new MediaStream([track]);
    document.body.appendChild(audioElement);
    audioElement.play();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const app = document.getElementById('app');
  const header = document.createElement('h1');
  header.textContent = 'Hello, AI Tinkerers!';
  header.id = 'main-header'
  app.appendChild(header);

  const start_button = document.createElement('button');
  start_button.textContent = 'Start';
  start_button.addEventListener('click', main);
  app.appendChild(start_button);

  console.log('Hello, AI Tinkerers!');
});

