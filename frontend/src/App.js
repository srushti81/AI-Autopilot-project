import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Commands from "./pages/Commands";
import Status from "./pages/Status";
import Assistant from "./pages/Assistant";
import Email from "./pages/Email";
import EmailAssistant from "./pages/EmailAssistant";


export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-[#0d0b16] text-white flex">
        <Sidebar />
        <main className="flex-1 p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/commands" element={<Commands />} />
            <Route path="/status" element={<Status />} />
            <Route path="/assistant" element={<Assistant />} />
            <Route path="/email" element={<Email />} />
            <Route path="/email" element={<EmailAssistant />} />

          </Routes>
        </main>
      </div>
    </Router>
  );
}
