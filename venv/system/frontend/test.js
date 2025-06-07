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
} // 视频采集
let videoStream;

async function startVideoRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    const videoElement = document.getElementById("camera-view");
    videoElement.srcObject = stream;
    videoStream = stream;

    // 每100ms捕获一帧
    setInterval(() => captureVideoFrame(videoElement), 100);
  } catch (error) {
    console.error("Error accessing camera:", error);
  }
}

function captureVideoFrame(videoElement) {
  const canvas = document.createElement("canvas");
  canvas.width = videoElement.videoWidth;
  canvas.height = videoElement.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

  const frameData = canvas.toDataURL("image/jpeg", 0.8);

  fetch("/api/video_frame", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      frame: frameData,
      timestamp: Date.now(),
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      updateVideoAnalysis(data.analysis);
    })
    .catch((error) => console.error("Error sending video frame:", error));
}

function updateVideoAnalysis(analysis) {
  if (!analysis.face_detected) {
    document.getElementById("face-status").textContent = "未检测到人脸";
    return;
  }

  document.getElementById("face-status").textContent = "检测到人脸";
  document.getElementById("emotion-tension").textContent =
    (analysis.emotion.tension * 100).toFixed(1) + "%";
  document.getElementById("eye-contact").textContent = analysis.eye_contact
    ? "是"
    : "否";
}
function analyzeResume() {
  const fileInput = document.getElementById("resume-upload");
  const file = fileInput.files[0];

  if (!file) {
    alert("请先上传简历");
    return;
  }

  const formData = new FormData();
  formData.append("resume", file);
  formData.append("job_description", "Python开发工程师");

  fetch("/api/analyze_resume", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("match-score").textContent =
        data.match_score.toFixed(1);
      document.getElementById("resume-text").value = data.resume_text;
    })
    .catch((error) => console.error("Error analyzing resume:", error));
}

function analyzeAnswer() {
  const question = document.getElementById("interview-question").value;
  const answer = document.getElementById("interview-answer").value;

  if (!question || !answer) {
    alert("请填写问题和回答");
    return;
  }

  fetch("/api/analyze_answer", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: question,
      answer: answer,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("star-score").textContent =
        data.analysis.star_score;
      document.getElementById("term-score").textContent =
        data.analysis.professional_term_score;
      document.getElementById("relevance-score").textContent =
        data.analysis.relevance_score;
      document.getElementById("llm-feedback").textContent =
        data.analysis.feedback;
    })
    .catch((error) => console.error("Error analyzing answer:", error));
}
function generateReport() {
  fetch("/api/combined_analysis")
    .then((response) => response.json())
    .then((data) => {
      const reportElement = document.getElementById("combined-report");
      reportElement.innerHTML = `
          <h3>语音分析</h3>
          <p>语速: ${data.analysis.audio.speaking_speed} 字/分钟</p>
          <p>停顿次数: ${data.analysis.audio.pause_count}</p>
          
          <h3>视频分析</h3>
          <p>紧张程度: ${(data.analysis.video.emotion.tension * 100).toFixed(
            1
          )}%</p>
          <p>眼神接触: ${
            data.analysis.video.eye_contact ? "良好" : "需要改进"
          }</p>
          
          <h3>内容分析</h3>
          <p>回答结构(STAR): ${data.analysis.text.star_score}/10</p>
          <p>专业术语: ${data.analysis.text.professional_term_score}/10</p>
      `;
    })
    .catch((error) => console.error("Error generating report:", error));
}
