# 🚀 AI Autopilot

AI Autopilot is a full-stack AI-powered web application that provides ChatGPT-like AI responses, secure authentication, email automation with attachments, and command execution — built with FastAPI + React (Vite).

## ✨ Features

*   **🤖 AI Chat Assistant (Groq / LLaMA)**
*   **🔐 JWT Authentication (Login & Signup)**
*   **📧 Email Sending with multiple attachments**
*   **🧠 Command History Tracking**
*   **📊 Dashboard & Status Pages**
*   **⚡ FastAPI Backend**
*   **⚛️ React + Vite Frontend**
*   **🌐 CORS-enabled API for frontend integration**

## 🛠 Tech Stack

### Frontend
*   React
*   Vite
*   React Router
*   Tailwind CSS
*   Fetch API

### Backend
*   FastAPI
*   Python 3.10+
*   MongoDB
*   JWT Authentication
*   Groq AI SDK
*   SMTP (Gmail)
*   Uvicorn

## 🚀 Getting Started

### Prerequisites
*   Node.js & npm
*   Python 3.8+

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/AI-Autopilot.git
cd AI-Autopilot
```

### 2️⃣ Backend Setup
Navigate to the backend folder and install dependencies:
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file in the `backend` folder with the following keys:
```env
GROQ_API_KEY=your_groq_api_key
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

Start the backend server:
```bash
uvicorn main:app --port 8000 --reload
```

### 3️⃣ Frontend Setup
Navigate to the frontend folder and install dependencies:
```bash
cd ../frontend
npm install
```

Start the frontend application:
```bash
npm start
```
The app will open at `http://localhost:3001`.

## 🌍 Deployment Guide

### Frontend (Vercel)
1.  Push your code to GitHub.
2.  Go to [Vercel](https://vercel.com) and import your `AI-Autopilot` repository.
3.  Set the **Root Directory** to `frontend`.
4.  Add Environment Variable:
    *   `REACT_APP_BACKEND_URL`: The URL of your deployed backend (e.g., `https://ai-autopilot-backend.onrender.com`).
5.  Deploy!

### Backend (Render)
1.  Go to [Render](https://render.com) and create a new **Web Service**.
2.  Connect your GitHub repository.
3.  Set **Root Directory** to `backend`.
4.  Set **Build Command**: `pip install -r requirements.txt`.
5.  Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`.
6.  Add Environment Variables (same as `.env` above).
7.  Deploy!

## 📷 Demo
*(Add a screenshot or video link here)*

## 📄 License
This project is licensed under the MIT License.
