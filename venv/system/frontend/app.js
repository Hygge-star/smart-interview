// 音频采集
let audioChunks = [];
let mediaRecorder;

async function startAudioRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        sendAudioChunk(event.data);
      }
    };

    mediaRecorder.start(1000); // 每1秒触发一次dataavailable
  } catch (error) {
    console.error("Error accessing microphone:", error);
  }
}

function sendAudioChunk(chunk) {
  const formData = new FormData();
  formData.append("audio", chunk, "audio_chunk.wav");
  formData.append("timestamp", Date.now());

  fetch("/api/audio_stream", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      updateTranscript(data.transcript);
      updateSpeechAnalysis(data.analysis);
    })
    .catch((error) => console.error("Error sending audio:", error));
}

function updateTranscript(text) {
  const transcriptElement = document.getElementById("transcript");
  transcriptElement.textContent += " " + text;
}

function updateSpeechAnalysis(analysis) {
  const speedElement = document.getElementById("speaking-speed");
  speedElement.textContent = analysis.speaking_speed.toFixed(1);

  const pauseElement = document.getElementById("pause-count");
  pauseElement.textContent = analysis.pause_count;
}
