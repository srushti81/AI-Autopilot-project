import React from "react";

export default function ChatBubble({ role = "assistant", text }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={`max-w-[80%] px-4 py-3 rounded-2xl break-words ${
          isUser ? "bg-purple-600 text-white rounded-br-none" : "bg-[#0f0d17] text-purple-200 rounded-bl-none border border-purple-700/20"
        }`}
      >
        <div className="whitespace-pre-wrap">{text}</div>
      </div>
    </div>
  );
}
