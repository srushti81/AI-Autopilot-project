# 🚀 AI Autopilot

An intelligent, voice-activated assistant designed to streamline daily tasks and boost productivity. Whether it’s drafting emails, answering queries, or executing commands, AI Autopilot handles it all with a modern, sleek interface.

## 🌟 Key Features

*   **📧 Smart Email Assistant:** Compose and send emails effortlessly using voice commands or text. Supports file attachments (documents, images, etc.) with a seamless drag-and-drop experience.
*   **🤖 AI-Powered Chat:** Integrated with the **Groq API (Llama 3.1)** to provide instant, intelligent responses to complex queries.
*   **🎙️ Voice Control:** Hands-free operation with real-time speech-to-text integration.
*   **⚡ Real-time Feedback:** Instant status updates and interactive chat bubbles.
*   **🎨 Modern UI:** A responsive, dark-themed dashboard built with React and Tailwind CSS.

## 🛠️ Tech Stack

*   **Frontend:** React.js, Tailwind CSS, Framer Motion, React Speech Recognition
*   **Backend:** Python, FastAPI, Uvicorn
*   **AI Integration:** Groq API (Llama-3.1-8b-instant)
*   **Email Service:** FastAPI-Mail, SMTP
*   **State Management:** React Hooks

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
uvicorn main:app --port 8001 --reload
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

## 📷 Demo
*(Add a screenshot or video link here)*

## 📄 License
This project is licensed under the MIT License.
