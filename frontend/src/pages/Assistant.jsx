import React, { useEffect, useRef, useState } from "react";
import ChatBubble from "../components/ChatBubble";

export default function Assistant() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesRef = useRef(null);

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem("ai_chat") || "[]");
    setMessages(saved);
  }, []);

  useEffect(() => {
    localStorage.setItem("ai_chat", JSON.stringify(messages));
    if (messagesRef.current) messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
  }, [messages]);

  const addMessage = (role, text) => {
    setMessages((m) => [...m, { role, text, t: Date.now() }]);
  };

  const run = async () => {
    if (!input.trim()) return;
    const userText = input.trim();
    addMessage("user", userText);
    setInput("");
    setLoading(true);

    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8001";
      const res = await fetch(`${API_URL}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: userText }),
      });
      const data = await res.json();
      const out = data.response ?? data.reply ?? data.output ?? JSON.stringify(data);
      addMessage("assistant", out);
      // optional TTS:
      if (window.speechSynthesis) {
        const utter = new SpeechSynthesisUtterance(out);
        utter.lang = "en-US";
        window.speechSynthesis.speak(utter);
      }
    } catch (err) {
      addMessage("assistant", "❌ Backend error or CORS.");
    } finally {
      setLoading(false);
    }
  };

  const clear = () => {
    setMessages([]);
    localStorage.removeItem("ai_chat");
  };

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">AI Assistant</h2>

      <div className="bg-[#171429] p-6 rounded-2xl border border-purple-700/20 shadow-xl flex flex-col">
        <div ref={messagesRef} className="max-h-96 overflow-auto mb-4 p-2">
          {messages.length === 0 && <div className="text-gray-400">No messages yet — say hi 👋</div>}
          {messages.map((m, i) => (
            <ChatBubble key={i} role={m.role} text={m.text} />
          ))}
          {loading && <div className="text-purple-300">Assistant is typing…</div>}
        </div>

        <div className="flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && run()}
            placeholder="Ask the assistant..."
            className="flex-1 p-3 rounded-xl bg-[#0f0d17] border border-purple-700/30 text-white"
          />
          <button onClick={run} className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-700">Send</button>
          <button onClick={clear} className="px-4 py-2 rounded-xl border border-purple-700/30 text-gray-300">Clear</button>
        </div>
      </div>
    </div>
  );
}
