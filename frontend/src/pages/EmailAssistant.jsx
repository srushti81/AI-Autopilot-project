import React, { useState } from "react";
import MicButton from "../components/MicButton";

export default function EmailAssistant() {
  const [to, setTo] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [files, setFiles] = useState([]); // ✅ array
  const [listening, setListening] = useState(false);
  const [status, setStatus] = useState("");

  let recognition;

  // -------------------------------------------------------
  // 🎤 Voice Input Setup
  // -------------------------------------------------------
  if ("webkitSpeechRecognition" in window) {
    const SpeechRecognition = window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
  }

  // -------------------------------------------------------
  // 🎤 Handle Mic Button
  // -------------------------------------------------------
  const startListening = () => {
    if (!recognition) {
      alert("Speech Recognition not supported");
      return;
    }

    setListening(true);
    recognition.start();

    recognition.onresult = async (event) => {
      setListening(false);
      const voiceText = event.results[0][0].transcript;
      setStatus("Generating email using AI...");

      const API_URL =
        import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";
      const token = localStorage.getItem("token");
      const headers = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      };

      const aiRes = await fetch(`${API_URL}/run`, {
        method: "POST",
        headers,
        body: JSON.stringify({ command: `Write an email: ${voiceText}` }),
      });

      const data = await aiRes.json();
      const aiEmail = data.response || "";

      const splitIndex = aiEmail.indexOf("\n");
      const aiSubject =
        splitIndex !== -1 ? aiEmail.substring(0, splitIndex) : aiEmail;
      const aiBody =
        splitIndex !== -1 ? aiEmail.substring(splitIndex + 1) : "";

      setSubject(aiSubject.replace("Subject:", "").trim());
      setMessage(aiBody.trim());
      setStatus("Email generated!");
    };

    recognition.onerror = () => {
      setListening(false);
      setStatus("Voice error — try again");
    };
  };

  // -------------------------------------------------------
  // 📎 Handle Attachments (FIXED)
  // -------------------------------------------------------
  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files); // ✅ CRITICAL FIX
    setFiles(selectedFiles);
  };

  // -------------------------------------------------------
  // 📩 Send Email
  // -------------------------------------------------------
  const sendEmail = async () => {
    if (!to || !subject || !message) {
      alert("Please fill all fields.");
      return;
    }

    setStatus("Sending email...");

    try {
      const API_URL =
        import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";
      const token = localStorage.getItem("token");
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const formData = new FormData();
      formData.append("recipient", to);
      formData.append("subject", subject);
      formData.append("body", message);

      // ✅ MULTIPLE FILES
      files.forEach((file) => {
        formData.append("attachments", file);
      });

      const emailRes = await fetch(`${API_URL}/send-email`, {
        method: "POST",
        headers,
        body: formData,
      });

      const data = await emailRes.json();

      if (emailRes.ok) {
        setStatus("Email sent successfully!");
        setFiles([]); // optional reset
      } else {
        setStatus("Failed to send email: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      setStatus("Network error or CORS: " + err.message);
    }
  };

  return (
    <div className="p-8 text-white">
      <h1 className="text-3xl font-bold text-purple-400 mb-6">
        Email Assistant
      </h1>

      <div className="space-y-6 bg-[#1c1a29] p-6 rounded-2xl shadow-lg border border-purple-700/30">
        <div>
          <label className="text-sm text-purple-300">Recipient Email</label>
          <input
            type="email"
            className="w-full p-3 mt-1 bg-[#151226] rounded-lg border border-purple-700/30"
            value={to}
            onChange={(e) => setTo(e.target.value)}
          />
        </div>

        <div>
          <label className="text-sm text-purple-300">Subject</label>
          <input
            type="text"
            className="w-full p-3 mt-1 bg-[#151226] rounded-lg border border-purple-700/30"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
        </div>

        <div>
          <label className="text-sm text-purple-300">Message</label>
          <textarea
            className="w-full p-3 mt-1 bg-[#151226] h-40 rounded-lg border border-purple-700/30"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          ></textarea>
        </div>

        {/* 📎 Attachments */}
        <div>
          <label className="text-sm text-purple-300">Attachments</label>
          <input
            type="file"
            multiple
            onChange={handleFileChange}
            className="w-full mt-2 text-sm text-purple-200"
          />

          {/* ✅ SHOW SELECTED FILES */}
          {files.length > 0 && (
            <ul className="mt-2 text-sm text-purple-300">
              {files.map((file, index) => (
                <li key={index}>📎 {file.name}</li>
              ))}
            </ul>
          )}
        </div>

        <button
          onClick={sendEmail}
          className="w-full p-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold"
        >
          Send Email
        </button>

        {status && <p className="text-purple-300 text-sm mt-2">{status}</p>}
      </div>

      <div className="fixed bottom-8 right-8">
        <MicButton onClick={startListening} listening={listening} />
      </div>
    </div>
  );
}
