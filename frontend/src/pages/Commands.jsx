import React, { useEffect, useState } from "react";

export default function Commands() {
  const [command, setCommand] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory(JSON.parse(localStorage.getItem("ai_history") || "[]"));
  }, []);

  const pushHistory = (entry) => {
    const newH = [...history, entry];
    setHistory(newH);
    localStorage.setItem("ai_history", JSON.stringify(newH));
  };

  const runCommand = async () => {
    if (!command.trim()) return;
    setLoading(true);
    setResponse("");
    try {
      const res = await fetch("http://127.0.0.1:8001/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command }),
      });
      const data = await res.json();
      // support different backends: try response.reply / response.response / data.output / data.reply
      const out = data.response ?? data.reply ?? data.output ?? JSON.stringify(data);
      const snippet = ("" + (out || "")).slice(0, 200);
      setResponse(out);
      pushHistory({ command, response: out, responseSnippet: snippet, t: Date.now() });
    } catch (err) {
      setResponse("❌ Backend error or CORS. Check backend server.");
    } finally {
      setLoading(false);
    }
  };

  const copyResponse = () => {
    if (!response) return;
    navigator.clipboard.writeText(response);
  };

  const clearHistory = () => {
    localStorage.removeItem("ai_history");
    setHistory([]);
  };

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">AI Commands</h2>

      <div className="bg-[#171429] p-6 rounded-2xl border border-purple-700/20 shadow-xl">
        <textarea
          rows="3"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Type an instruction, e.g. Summarize this text..."
          className="w-full p-3 rounded-xl bg-[#0f0d17] border border-purple-700/30 text-white mb-4"
        />

        <div className="flex gap-3">
          <button
            onClick={runCommand}
            className="flex-1 py-3 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-semibold disabled:opacity-60"
            disabled={loading}
          >
            {loading ? "Running..." : "Execute"}
          </button>

          <button
            onClick={() => {
              setCommand("");
              setResponse("");
            }}
            className="px-4 py-3 rounded-xl border border-purple-700/30 text-gray-300"
          >
            Clear
          </button>
        </div>

        {response && (
          <div className="mt-5 p-4 bg-black/30 rounded-xl border border-purple-700/30">
            <div className="flex justify-between items-start">
              <h3 className="text-purple-300 font-semibold">Response</h3>
              <div className="flex gap-2">
                <button onClick={copyResponse} className="text-sm text-gray-300 hover:text-white">
                  Copy
                </button>
              </div>
            </div>
            <pre className="mt-3 text-gray-300 whitespace-pre-wrap max-h-60 overflow-auto">{response}</pre>
          </div>
        )}

        <div className="mt-6">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm text-purple-300">History</h4>
            <button onClick={clearHistory} className="text-sm text-red-400">Clear history</button>
          </div>
          <div className="space-y-3 max-h-40 overflow-auto">
            {history.length === 0 && <div className="text-gray-400">No history yet</div>}
            {history.slice().reverse().map((h, i) => (
              <div key={i} className="p-3 rounded-lg bg-black/20 border border-purple-800/20">
                <div className="text-sm text-gray-200">{h.command}</div>
                <div className="text-xs text-purple-300 mt-1">{h.responseSnippet}</div>
                <div className="text-xs text-gray-500 mt-1">{new Date(h.t).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
