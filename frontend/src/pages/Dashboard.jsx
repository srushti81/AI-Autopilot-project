import React, { useEffect, useState } from "react";

export default function Dashboard() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const h = JSON.parse(localStorage.getItem("ai_history") || "[]");
    setHistory(h);
  }, []);

  const total = history.length;
  const last = history.length ? history[history.length - 1].responseSnippet : "—";

  // quick sparkline from history response lengths
  const points = history.slice(-12).map((h) => Math.min(100, (h.response || "").length));

  const sparkPath = points.length
    ? points
        .map((p, i) => {
          const x = (i / (points.length - 1 || 1)) * 100;
          const y = 100 - (p / 100) * 100;
          return `${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
        })
        .join(" ")
    : "";

  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-[#171429] p-6 rounded-2xl border border-purple-700/20 shadow-xl">
          <h3 className="text-lg text-purple-300 font-semibold mb-2">Commands Run</h3>
          <div className="text-3xl font-bold">{total}</div>
          <div className="text-sm text-gray-400 mt-2">Total commands stored in local history</div>
        </div>

        <div className="bg-[#171429] p-6 rounded-2xl border border-purple-700/20 shadow-xl">
          <h3 className="text-lg text-purple-300 font-semibold mb-2">Last Response</h3>
          <div className="text-gray-300">{last}</div>
        </div>

        <div className="bg-[#171429] p-6 rounded-2xl border border-purple-700/20 shadow-xl">
          <h3 className="text-lg text-purple-300 font-semibold mb-2">Activity</h3>
          <svg viewBox="0 0 100 100" className="w-full h-16">
            <path d={sparkPath} fill="none" stroke="#a78bfa" strokeWidth="1.5" />
          </svg>
        </div>
      </div>

      <div className="bg-[#171429] p-6 rounded-2xl border border-purple-700/20 shadow-xl">
        <h3 className="text-xl text-purple-300 mb-3">Recent Logs</h3>
        {history.length === 0 ? (
          <p className="text-gray-400">No commands run yet — go to Commands page.</p>
        ) : (
          <ul className="space-y-3 max-h-64 overflow-auto">
            {history.slice().reverse().map((h, idx) => (
              <li key={idx} className="p-3 rounded-lg bg-black/30 border border-purple-800/20">
                <div className="text-sm text-gray-300">{h.command}</div>
                <div className="text-xs text-purple-300 mt-1">{h.responseSnippet}</div>
                <div className="text-xs text-gray-500 mt-1">{new Date(h.t).toLocaleString()}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
