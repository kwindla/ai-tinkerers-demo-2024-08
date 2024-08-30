
import { DailyVoiceClient } from "realtime-ai-daily";
import { LLMHelper } from "realtime-ai";

import { simpleConfig } from "./rtvi.simple-config.ts";
import { visionConfig } from "./rtvi.vision-config.ts";

window.voiceClient;
window.micEnabled = true;
window.camEnabled = false;

function main(withCam) {
  window.camEnabled = withCam;

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
    enableMic: window.micEnabled,
    enableCam: window.camEnabled,
    callbacks:{
      onBotReady: botReadyHandler,
      onTrackStarted: trackStartedHandler
    },

    //
    // the services the bot we are talking to supports
    //
    services: {
       llm: "together",
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
  window.voiceClient = voiceClient;
  voiceClient.registerHelper("llm", llmHelper);
  voiceClient.start()
}

async function botReadyHandler() {
  console.log('Bot ready');
  const header = document.getElementById('main-header');
  header.textContent = 'Connected ...';
  if (window.camEnabled) {
    await window.voiceClient.updateConfig(visionConfig);
  } else {
    await window.voiceClient.updateConfig(simpleConfig);
  }
  window.voiceClient.getHelper('llm').run();
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
  header.textContent = 'Hello, YC Live!';
  header.id = 'main-header'
  app.appendChild(header);

  const start_button_1 = document.createElement('button');
  start_button_1.textContent = 'Start Simple';
  start_button_1.addEventListener('click', () => main(false));
  app.appendChild(start_button_1);

  const start_button_2 = document.createElement('button');
  start_button_2.textContent = 'Start With Cam On';
  start_button_2.addEventListener('click', () => main(true));
  app.appendChild(start_button_2);

  const toggle_mic_button = document.createElement('button');
  toggle_mic_button.textContent = 'mute/unmute';
  toggle_mic_button.addEventListener('click', () => {
    window.micEnabled = !window.micEnabled;
    console.log('toggle mic to', window.micEnabled);
    window.voiceClient.enableMic(window.micEnabled);
  });
  app.appendChild(toggle_mic_button);
});


//   
