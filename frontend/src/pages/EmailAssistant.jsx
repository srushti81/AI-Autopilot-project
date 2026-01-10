import React, { useState } from "react";
import MicButton from "../components/MicButton";

export default function EmailAssistant() {
  const [to, setTo] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");

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

      // Send voice text to backend to generate email content
      const API_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8001";
      const aiRes = await fetch(`${API_URL}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: `Write an email: ${voiceText}` }),
      });

      const data = await aiRes.json();
      const aiEmail = data.response;

      // Basic extraction: split subject + body
      const splitIndex = aiEmail.indexOf("\n");
      const aiSubject = aiEmail.substring(0, splitIndex).replace("Subject: ", "");
      const aiBody = aiEmail.substring(splitIndex + 1);

      setSubject(aiSubject.trim());
      setMessage(aiBody.trim());
      setStatus("Email generated!");
    };

    recognition.onerror = () => {
      setListening(false);
      setStatus("Voice error — try again");
    };
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
      const API_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8001";
      const formData = new FormData();
      formData.append("recipient", to);
      formData.append("subject", subject);
      formData.append("body", message);

      const emailRes = await fetch(`${API_URL}/send-email`, {
        method: "POST",
        body: formData,
      });

      const data = await emailRes.json();

      if (emailRes.ok) {
        setStatus("Email sent successfully!");
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

      {/* Email Input */}
      <div className="space-y-6 bg-[#1c1a29] p-6 rounded-2xl shadow-lg border border-purple-700/30">
        <div>
          <label className="text-sm text-purple-300">Recipient Email</label>
          <input
            type="email"
            className="w-full p-3 mt-1 bg-[#151226] rounded-lg border border-purple-700/30 focus:border-purple-500 outline-none"
            placeholder="example@gmail.com"
            value={to}
            onChange={(e) => setTo(e.target.value)}
          />
        </div>

        <div>
          <label className="text-sm text-purple-300">Subject</label>
          <input
            type="text"
            className="w-full p-3 mt-1 bg-[#151226] rounded-lg border border-purple-700/30 focus:border-purple-500 outline-none"
            placeholder="Enter subject or use mic"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
        </div>

        <div>
          <label className="text-sm text-purple-300">Message</label>
          <textarea
            className="w-full p-3 mt-1 bg-[#151226] h-40 rounded-lg border border-purple-700/30 focus:border-purple-500 outline-none"
            placeholder="Write email or use mic"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          ></textarea>
        </div>

        <button
          onClick={sendEmail}
          className="w-full p-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition"
        >
          Send Email
        </button>

        {status && (
          <p className="text-purple-300 text-sm mt-2">
            {status}
          </p>
        )}
      </div>

      {/* Floating Mic Button */}
      <div className="fixed bottom-8 right-8">
        <MicButton onClick={startListening} listening={listening} />
      </div>
    </div>
  );
}
