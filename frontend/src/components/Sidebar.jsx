import React from "react";
import { Link, useLocation } from "react-router-dom";

export default function Sidebar({ isOpen, onClose }) {
  const { pathname } = useLocation();

  const menu = [
    { name: "Dashboard", path: "/" },
    { name: "Commands", path: "/commands" },
    { name: "System Status", path: "/status" },
    { name: "Assistant", path: "/assistant" },
    { name: "Email Assistant", path: "/email-assistant" },
  ];

  const linkClass = (isActive) =>
    `block w-full text-left p-3 rounded-xl transition-all duration-200 ${isActive
      ? "text-white bg-gradient-to-r from-purple-600 to-indigo-600 shadow-md translate-x-1"
      : "text-gray-400 hover:text-white hover:bg-white/5"
    }`;

  // Overlay for mobile
  const overlayClass = isOpen
    ? "fixed inset-0 bg-black/50 z-20 md:hidden backdrop-blur-sm"
    : "hidden";

  // Sidebar container
  const sidebarClass = `
    fixed md:static inset-y-0 left-0 z-30 w-64 bg-[#151226] border-r border-white/5 p-6 flex flex-col transition-transform duration-300 ease-in-out
    ${isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
  `;

  return (
    <>
      {/* Mobile Overlay */}
      <div className={overlayClass} onClick={onClose} />

      {/* Sidebar */}
      <aside className={sidebarClass}>
        <div className="flex items-center justify-between mb-10">
          <h1 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 tracking-wider">
            AUTOPILOT
          </h1>
          {/* Close button for mobile */}
          <button onClick={onClose} className="md:hidden text-gray-400 hover:text-white">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <nav className="space-y-2 flex-1">
          {menu.map((m) => (
            <Link
              key={m.path}
              to={m.path}
              className={linkClass(pathname === m.path)}
              onClick={() => onClose && onClose()} // Close on click (mobile)
            >
              <div className="flex items-center">
                {/* Optional: Add icons here if you want */}
                <span className="font-medium">{m.name}</span>
              </div>
            </Link>
          ))}
        </nav>

        <div className="mt-auto pt-6 border-t border-white/5 space-y-4">
          <button
            onClick={() => {
              localStorage.removeItem("token");
              localStorage.removeItem("user");
              window.location.href = "/login";
            }}
            className="w-full flex items-center justify-center p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500 hover:text-white transition duration-200 text-sm font-medium"
          >
            Logout
          </button>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-center text-xs font-bold">AI</div>
            <div className="text-sm text-gray-400">
              <div className="text-white font-medium">User</div>
              <div className="text-xs">v1.0.0</div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
