let mediaRecorder,
  audioChunks = [];
const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const userText = document.getElementById("userText");
const botAnswer = document.getElementById("botAnswer");
const botAudio = document.getElementById("botAudio");
const statusMsg = document.getElementById("statusMsg");

function setStatus(msg, color = "#a09cff") {
  statusMsg.textContent = msg;
  statusMsg.style.color = color;
  statusMsg.style.transition = "color 0.2s";
}

recordBtn.onclick = async () => {
  audioChunks = [];
  setStatus("🎙️ Recording... Speak your question.", "#7f6fff");
  let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.start();
  recordBtn.disabled = true;
  stopBtn.disabled = false;

  mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
};

stopBtn.onclick = async () => {
  setStatus("⏳ Processing your question...", "#ffb86c");
  mediaRecorder.stop();
  stopBtn.disabled = true;
  recordBtn.disabled = false;

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    let formData = new FormData();
    formData.append("audio", audioBlob, "question.wav");

    userText.textContent = "";
    botAnswer.textContent = "";
    botAudio.src = "";

    setStatus("📝 Transcribing...", "#7f6fff");
    try {
      const response = await fetch("http://localhost:5000/ask", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (data.error) {
        setStatus("❌ " + data.error, "#ff6b81");
        userText.textContent = "";
        botAnswer.textContent = "";
        return;
      }
      setStatus("✅ Success! Listen to your answer below.", "#43e97b");
      userText.textContent = data.transcript;
      botAnswer.textContent = data.answer;
      botAudio.src = "data:audio/mp3;base64," + data.audio_base64;
      botAudio.play();
    } catch (err) {
      setStatus("❌ Network or server error.", "#ff6b81");
    }
  };
};
