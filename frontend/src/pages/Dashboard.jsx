import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

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
    <div className="p-8 min-h-screen bg-gradient-to-br from-[#0f0c29] via-[#302b63] to-[#24243e] text-white">
      <header className="mb-8">
        <h2 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
          Dashboard
        </h2>
        <p className="text-gray-400 mt-2">Overview of your AI autopilot activity</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Card 1 */}
        <div className="bg-white/5 backdrop-blur-xl p-6 rounded-2xl border border-white/10 shadow-lg hover:bg-white/10 transition duration-300">
          <h3 className="text-lg text-purple-300 font-semibold mb-2">Commands Run</h3>
          <div className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-300">
            {total}
          </div>
          <div className="text-sm text-gray-400 mt-2">Total stored commands</div>
        </div>

        {/* Card 2 */}
        <div className="bg-white/5 backdrop-blur-xl p-6 rounded-2xl border border-white/10 shadow-lg hover:bg-white/10 transition duration-300">
          <h3 className="text-lg text-purple-300 font-semibold mb-2">Last Response</h3>
          <div className="text-gray-200 truncate italic">"{last}"</div>
          <div className="text-xs text-gray-500 mt-2">Most recent output</div>
        </div>

        {/* Card 3 */}
        <div className="bg-white/5 backdrop-blur-xl p-6 rounded-2xl border border-white/10 shadow-lg hover:bg-white/10 transition duration-300">
          <h3 className="text-lg text-purple-300 font-semibold mb-2">Activity Pulse</h3>
          <div className="h-16 w-full flex items-end">
            <svg viewBox="0 0 100 100" className="w-full h-full overflow-visible">
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#8b5cf6" />
                  <stop offset="100%" stopColor="#ec4899" />
                </linearGradient>
              </defs>
              <path
                d={sparkPath}
                fill="none"
                stroke="url(#gradient)"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="drop-shadow-[0_0_10px_rgba(139,92,246,0.5)]"
              />
            </svg>
          </div>
        </div>
      </div>

      <div className="bg-white/5 backdrop-blur-xl p-6 rounded-3xl border border-white/10 shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-2xl font-bold text-white">Recent Logs</h3>
          <Link
            to="/commands"
            className="text-sm text-purple-400 hover:text-purple-300 transition"
          >
            View All &rarr;
          </Link>
        </div>

        {history.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🚀</div>
            <p className="text-xl text-gray-300 font-medium">Ready for takeoff?</p>
            <p className="text-gray-500 mb-6">Run your first command to see data here.</p>
            <Link
              to="/commands"
              className="inline-block bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-3 px-8 rounded-full shadow-lg hover:shadow-purple-500/50 transition transform hover:-translate-y-1"
            >
              Start Autopilot
            </Link>
          </div>
        ) : (
          <ul className="space-y-4">
            {history
              .slice()
              .reverse()
              .map((h, idx) => (
                <li
                  key={idx}
                  className="group flex items-center justify-between p-4 rounded-xl bg-black/20 border border-white/5 hover:bg-white/10 hover:border-purple-500/30 transition duration-200"
                >
                  <div className="flex-1 min-w-0 mr-4">
                    <div className="text-base font-medium text-white truncate group-hover:text-purple-300 transition">
                      {h.command}
                    </div>
                    <div className="text-xs text-gray-400 mt-1 truncate max-w-md">
                      {h.responseSnippet}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 whitespace-nowrap font-mono">
                    {new Date(h.t).toLocaleString()}
                  </div>
                </li>
              ))}
          </ul>
        )}
      </div>
    </div>
  );
}
