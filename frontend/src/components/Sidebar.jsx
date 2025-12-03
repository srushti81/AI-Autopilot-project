import React from "react";
import { Link, useLocation } from "react-router-dom";

export default function Sidebar() {
  const { pathname } = useLocation();

  const menu = [
    { name: "Dashboard", path: "/" },
    { name: "Commands", path: "/commands" },
    { name: "System Status", path: "/status" },
    { name: "Assistant", path: "/assistant" },
    { name: "Email Assistant", path: "/email" },   // ⬅️ Added here
  ];

  const linkClass = (isActive) =>
    `block w-full text-left p-2 rounded-lg transition ${
      isActive
        ? "text-purple-400 bg-purple-800/20 font-semibold"
        : "text-gray-300 hover:text-purple-400"
    }`;

  return (
    <aside className="w-64 bg-[#151226] border-r border-purple-700/30 p-6 hidden md:flex flex-col">
      <h1 className="text-2xl font-bold mb-10 text-purple-400">AI AUTOPILOT</h1>

      <nav className="space-y-3">
        {menu.map((m) => (
          <Link
            key={m.path}
            to={m.path}
            className={linkClass(pathname === m.path)}
          >
            {m.name}
          </Link>
        ))}
      </nav>

      <div className="mt-auto text-sm text-purple-400/60">
        v1.0 • Stable
      </div>
    </aside>
  );
}
