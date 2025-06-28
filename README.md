🤖 AI Appointment Booking Assistant with Google Calendar
This is a conversational AI agent built with FastAPI, LangGraph, and Streamlit that helps users book appointments directly into Google Calendar through natural language chat.

🔍 Overview
The AI agent is capable of:

Understanding natural user input like:

“Book a meeting between 3-5 PM tomorrow”
“Do I have any free time this Friday?”
“Schedule a call next week afternoon”

Extracting intent, date, and time

Checking calendar availability

Booking confirmed meetings

Responding interactively via a Streamlit chat interface

🛠 Tech Stack
Layer	Tool/Framework
Backend	Python + FastAPI
Agent Logic	LangGraph
Calendar API	Google Calendar API
Frontend	Streamlit

⚙️ Project Structure
bash
Copy
Edit
calendar_bot/
├── app.py                # Streamlit UI
├── main.py               # FastAPI backend (Google Calendar API)
├── langgraph_agent.py    # LangGraph conversational agent
├── google_calendar.py    # Calendar API logic
├── requirements.txt
├── README.md
├── .gitignore
🚀 Getting Started (Local Development)
🔧 Prerequisites
Python 3.8+

Google Cloud Project with Calendar API enabled

OAuth 2.0 credentials (credentials.json)

🔨 Setup Instructions
Clone the repo

bash
Copy
Edit
git clone https://github.com/your-username/calendar-bot.git
cd calendar-bot
Create virtual environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Add your Google credentials

Place your credentials.json file in the project root (DO NOT COMMIT THIS FILE).

Run FastAPI backend

bash
Copy
Edit
uvicorn main:app --reload
Run Streamlit frontend

bash
Copy
Edit
streamlit run app.py
🌐 Deployment
🔧 FastAPI deployed on Render

💬 Streamlit UI deployed on Streamlit Cloud

You can interact with the bot live here:
👉 LIVE STREAMLIT APP
👉 GitHub Repository

🧠 Example Prompts Supported
“Schedule a meeting tomorrow afternoon.”

“Am I free on Friday between 2-4 PM?”

“Book a call next week evening.”

“Check availability this Friday morning.”

❗ Notes
App is currently in test mode, so only added test users can access the Google Calendar functionality.

token.json is auto-generated after first login to cache credentials.

🙋 Author
Rajan Kumar Mourya
Passionate about AI, full-stack systems, and real-world automation.

