import React from "react";

export default function Status() {
  return (
    <div>
      <h2 className="text-3xl font-bold mb-6">System Status</h2>
      <div className="bg-[#171429] p-6 rounded-2xl border border-purple-700/20 shadow-xl">
        <h3 className="text-xl text-purple-300 font-semibold mb-2">All Systems</h3>
        <p className="text-gray-300">Operational ✔️</p>
        <p className="text-gray-400 mt-2 text-sm">Model response: <span className="text-purple-300">0.41s</span></p>
      </div>
    </div>
  );
}
