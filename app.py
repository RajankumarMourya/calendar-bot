
import streamlit as st
from langgraph_agent import build_agent

st.set_page_config(page_title="AI Appointment Assistant", layout="centered")
st.title("🗓️ AI Appointment Booking Assistant")

# Keep agent in session
if "agent" not in st.session_state:
    st.session_state.agent = build_agent()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Type your appointment request here...")

if user_input:
    st.session_state.chat_history.append(("You", user_input))
    result = st.session_state.agent.invoke({"user_input": user_input})
    st.session_state.chat_history.append(("Assistant", result["final_response"]))

for sender, message in st.session_state.chat_history:
    st.chat_message(sender).write(message)
