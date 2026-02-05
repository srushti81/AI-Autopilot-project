import React, { useState } from "react";
import MicButton from "../components/MicButton";

export default function Email() {
  const [to, setTo] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [files, setFiles] = useState([]);
  const [listening, setListening] = useState(false);
  const [status, setStatus] = useState("");

  // ✅ HARDCODED backend (SAFE for frontend)
  const API_BASE_URL = "https://ai-autopilot-back.onrender.com";

  let recognition;
  if ("webkitSpeechRecognition" in window) {
    const SpeechRecognition = window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
  }

  // 🎤 Voice input
  const startListening = () => {
    if (!recognition) {
      alert("Speech Recognition not supported");
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      setStatus("Please login again");
      return;
    }

    setListening(true);
    recognition.start();

    recognition.onresult = async (event) => {
      setListening(false);
      const voiceText = event.results[0][0].transcript;
      setStatus("Generating email...");

      try {
        const aiRes = await fetch(`${API_BASE_URL}/run`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            command: `Write a professional email: ${voiceText}`,
          }),
        });

        if (!aiRes.ok) throw new Error("AI request failed");

        const data = await aiRes.json();
        const aiEmail = data.response || "";

        const splitIndex = aiEmail.indexOf("\n");
        const aiSubject =
          splitIndex !== -1 ? aiEmail.slice(0, splitIndex) : aiEmail;
        const aiBody =
          splitIndex !== -1 ? aiEmail.slice(splitIndex + 1) : "";

        setSubject(aiSubject.replace("Subject:", "").trim());
        setMessage(aiBody.trim());
        setStatus("Email generated ✔️");
      } catch (err) {
        console.error(err);
        setStatus("Failed to generate email");
      }
    };

    recognition.onerror = () => {
      setListening(false);
      setStatus("Voice error");
    };
  };

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  // 📩 SEND EMAIL (FIXED)
  const sendEmail = async () => {
    if (!to || !subject || !message) {
      alert("Fill all fields");
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      setStatus("Please login again");
      return;
    }

    setStatus("Sending email...");

    try {
      const formData = new FormData();
      formData.append("recipient", to);
      formData.append("subject", subject);
      formData.append("body", message);
      files.forEach((file) => formData.append("attachments", file));

      const emailRes = await fetch(`${API_BASE_URL}/send-email`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      // ✅ THIS WAS THE BUG
      if (!emailRes.ok) {
        const errText = await emailRes.text();
        throw new Error(errText);
      }

      setStatus("Email sent successfully ✅");
      setFiles([]);
    } catch (err) {
      console.error("SEND EMAIL ERROR:", err);
      setStatus("Failed to send email ❌");
    }
  };

  return (
    <div className="p-8 text-white">
      <h2 className="text-3xl font-bold mb-6">Email Assistant</h2>

      <div className="space-y-6 bg-[#1c1a29] p-6 rounded-2xl border border-purple-700/30">
        <input
          placeholder="Recipient"
          value={to}
          onChange={(e) => setTo(e.target.value)}
          className="w-full p-3 bg-[#151226] rounded-lg"
        />

        <input
          placeholder="Subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className="w-full p-3 bg-[#151226] rounded-lg"
        />

        <textarea
          placeholder="Message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="w-full p-3 h-40 bg-[#151226] rounded-lg"
        />

        <input type="file" multiple onChange={handleFileChange} />

        <button
          onClick={sendEmail}
          className="w-full p-3 bg-purple-600 rounded-lg"
        >
          Send Email
        </button>

        {status && <p className="text-purple-300 text-sm">{status}</p>}
      </div>

      <div className="fixed bottom-8 right-8">
        <MicButton onClick={startListening} listening={listening} />
      </div>
    </div>
  );
}
