import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Commands from "./pages/Commands";
import Status from "./pages/Status";
import Assistant from "./pages/Assistant";
import Email from "./pages/Email.jsx";
import EmailAssistant from "./pages/EmailAssistant";
import Login from "./pages/Login";
import Signup from "./pages/Signup";

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" />;
};

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected Routes with Layout */}
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <div className="flex h-screen bg-[#0f0c29] text-white overflow-hidden">
                {/* Sidebar (Responsive) */}
                <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

                {/* Main Content Area */}
                <div className="flex-1 flex flex-col h-full overflow-hidden relative">

                  {/* Mobile Header */}
                  <header className="md:hidden flex items-center p-4 bg-[#151226] border-b border-white/5 z-10">
                    <button
                      onClick={() => setIsSidebarOpen(true)}
                      className="text-gray-300 hover:text-white p-2"
                    >
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
                    </button>
                    <span className="ml-4 font-bold text-lg text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">AI Autopilot</span>
                  </header>

                  <main className="flex-1 overflow-auto bg-[#0f0c29]">
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/commands" element={<Commands />} />
                      <Route path="/status" element={<Status />} />
                      <Route path="/assistant" element={<Assistant />} />
                      <Route path="/email" element={<Email />} />
                      <Route path="/email-assistant" element={<EmailAssistant />} />
                    </Routes>
                  </main>
                </div>
              </div>
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
