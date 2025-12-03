import React, { useState, useEffect, useCallback } from "react";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

export default function Email() {
  const [to, setTo] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState("");
  const [attachments, setAttachments] = useState([]);

  const handleFileChange = (e) => {
    setAttachments(Array.from(e.target.files));
  };

  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } = useSpeechRecognition();

  const sendEmail = useCallback(async () => {
    console.log("Sending email...");
    console.log("Current attachments state:", attachments);

    setStatus("Sending...");

    const formData = new FormData();
    formData.append("recipient", to);
    formData.append("subject", subject);
    formData.append("body", message);
    attachments.forEach((file) => {
      console.log("Appending file:", file.name);
      formData.append("attachments", file);
    });

    // Debug: Log FormData entries
    for (var pair of formData.entries()) {
        console.log(pair[0]+ ', ' + pair[1]); 
    }

    const response = await fetch("http://localhost:8001/send-email", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      setStatus("✔ Email sent successfully!");
    } else {
      setStatus("❌ Error: " + (data.error || "Unknown error"));
    }
  }, [to, subject, message, attachments]);

  useEffect(() => {
    if (transcript) {
      setMessage(transcript);
    }
  }, [transcript]);

  useEffect(() => {
    if (!listening && transcript) {
      sendEmail();
    }
  }, [listening, transcript, sendEmail]);

  return (
    <div className="text-white">
      <h2 className="text-3xl font-bold mb-6">Email Assistant</h2>

      <div className="bg-[#171429] p-6 rounded-2xl border border-purple-700/20 shadow-xl space-y-4">
        
        <input 
          className="w-full p-3 bg-[#0f0d17] border border-purple-700/30 rounded-xl"
          placeholder="Recipient Email"
          value={to}
          onChange={(e) => setTo(e.target.value)}
        />

        <input 
          className="w-full p-3 bg-[#0f0d17] border border-purple-700/30 rounded-xl"
          placeholder="Subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />

        <textarea 
          className="w-full p-3 bg-[#0f0d17] border border-purple-700/30 rounded-xl h-40"
          placeholder="Email message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        ></textarea>

        <input 
          type="file"
          multiple
          className="w-full p-3 bg-[#0f0d17] border border-purple-700/30 rounded-xl text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
          onChange={handleFileChange}
        />
        {attachments.length > 0 && (
          <div className="mt-2 text-gray-400">
            <p className="font-semibold">Selected Files:</p>
            <ul className="list-disc list-inside">
              {attachments.map((file, index) => (
                <li key={index}>{file.name}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex items-center space-x-4">
          {browserSupportsSpeechRecognition ? (
            <>
              <button 
                onClick={SpeechRecognition.startListening}
                className="p-3 bg-green-600 hover:bg-green-700 transition rounded-xl font-semibold"
              >
                Start Voice Input
              </button>
              <button 
                onClick={SpeechRecognition.stopListening}
                className="p-3 bg-red-600 hover:bg-red-700 transition rounded-xl font-semibold"
              >
                Stop Voice Input
              </button>
              <button 
                onClick={() => { resetTranscript(); setMessage(""); }}
                className="p-3 bg-gray-600 hover:bg-gray-700 transition rounded-xl font-semibold"
              >
                Reset Transcript
              </button>
              <p className="text-purple-300">Listening: {listening ? 'on' : 'off'}</p>
            </>
          ) : (
            <p className="text-red-400">Browser doesn't support speech recognition. Please type your message.</p>
          )}
        </div>

        <button 
          onClick={sendEmail}
          className="w-full p-3 bg-purple-600 hover:bg-purple-700 transition rounded-xl font-semibold"
        >
          Send Email
        </button>

        <p className="text-purple-300">{status}</p>
      </div>
      
    </div>
  );
}
