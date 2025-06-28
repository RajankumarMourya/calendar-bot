# langgraph_agent.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal, Optional
from datetime import datetime, timedelta
import re
import requests

# ---------- 1. Define the Agent's State ----------
class AgentState(TypedDict):
    user_input: str
    intent: Optional[Literal["check", "book", "unknown"]]
    date: Optional[str]
    time_range: Optional[str]
    available: Optional[bool]
    booked: Optional[bool]
    final_response: Optional[str]

# ---------- 2. Node: Intent Parser ----------
def parse_intent_node(state: AgentState) -> AgentState:
    user_input = state["user_input"].lower()
    if "book" in user_input or "schedule" in user_input:
        state["intent"] = "book"
    elif "free" in user_input or "available" in user_input:
        state["intent"] = "check"
    else:
        state["intent"] = "unknown"
    return state

def extract_datetime_node(state: AgentState) -> AgentState:
    user_input = state["user_input"].lower()
    now = datetime.now()

    # Handle common keywords
    if "tomorrow" in user_input:
        state["date"] = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "today" in user_input:
        state["date"] = now.strftime("%Y-%m-%d")
    elif "friday" in user_input:
        days_ahead = (4 - now.weekday() + 7) % 7
        state["date"] = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    elif "next week" in user_input:
        state["date"] = (now + timedelta(days=7)).strftime("%Y-%m-%d")
    else:
        state["date"] = state.get("date")

    # Handle vague times
    if "afternoon" in user_input:
        state["time_range"] = "13-17"
    elif "evening" in user_input:
        state["time_range"] = "17-20"
    elif "morning" in user_input:
        state["time_range"] = "9-12"
    else:
        # Fallback to regex like 3-5 or 3 to 5
        match = re.search(r'(\d{1,2})\s*[-to]+\s*(\d{1,2})', user_input)
        if match:
            state["time_range"] = f"{match.group(1)}-{match.group(2)}"

    return state


    # Basic regex for time range like "3 to 5 pm"
    time_match = re.search(r'(\d{1,2})\s*[-to]+\s*(\d{1,2})\s*(am|pm)?', user_input)
    if time_match:
        time_range = f"{time_match.group(1)}-{time_match.group(2)}"
        state["time_range"] = time_range

    # Basic date logic
    if "tomorrow" in user_input:
        state["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "today" in user_input:
        state["date"] = datetime.now().strftime("%Y-%m-%d")
    elif "friday" in user_input:
        today = datetime.now()
        days_ahead = (4 - today.weekday() + 7) % 7
        state["date"] = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    else:
        state["date"] = state.get("date", None)

    return state

# ---------- 4. Node: Calendar API via FastAPI ----------
API_BASE = "http://localhost:8000"  # Replace with deployed URL if hosted

def check_availability_node(state: AgentState) -> AgentState:
    try:
        start, end = [int(x.strip()) for x in state["time_range"].split("-")]
        res = requests.get(f"{API_BASE}/check", params={
            "date": state["date"],
            "start_hour": start,
            "end_hour": end
        })
        state["available"] = res.json().get("available", False)
    except Exception as e:
        print("Error checking availability:", e)
        state["available"] = False
    return state

def book_slot_node(state: AgentState) -> AgentState:
    try:
        start, end = [int(x.strip()) for x in state["time_range"].split("-")]
        res = requests.post(f"{API_BASE}/book", json={
            "date": state["date"],
            "start_hour": start,
            "end_hour": end,
            "summary": "Meeting via AI Bot"
        })
        state["booked"] = res.json().get("booked", False)
    except Exception as e:
        print("Error booking meeting:", e)
        state["booked"] = False
    return state

# ---------- 5. Node: Generate Response ----------
def respond_node(state: AgentState) -> AgentState:
    if not state.get("date") or not state.get("time_range"):
        state["final_response"] = "🤖 I need a date and time to check or book your meeting."
        return state

    if state["intent"] == "book":
        if state.get("booked"):
            state["final_response"] = f"✅ Your meeting has been booked on {state['date']} at {state['time_range']}."
        else:
            state["final_response"] = f"❌ You're not free on {state['date']} from {state['time_range']}."
    elif state["intent"] == "check":
        if state.get("available"):
            state["final_response"] = f"✅ You're free on {state['date']} at {state['time_range']}."
        else:
            state["final_response"] = f"❌ You're not free on {state['date']} from {state['time_range']}."
    else:
        state["final_response"] = "🤖 Sorry, I couldn't understand your request."

    return state


# ---------- 6. Build LangGraph ----------
def build_agent():
    builder = StateGraph(AgentState)

    builder.add_node("parse_intent", parse_intent_node)
    builder.add_node("extract_datetime", extract_datetime_node)
    builder.add_node("check_availability", check_availability_node)
    builder.add_node("book_slot", book_slot_node)
    builder.add_node("respond", respond_node)

    builder.set_entry_point("parse_intent")
    builder.add_edge("parse_intent", "extract_datetime")
    builder.add_edge("extract_datetime", "check_availability")
    builder.add_edge("check_availability", "book_slot")
    builder.add_edge("book_slot", "respond")
    builder.add_edge("respond", END)

    return builder.compile()

# ---------- 7. Optional CLI Test ----------
if __name__ == "__main__":
    agent = build_agent()
    while True:
        user_input = input("You: ")
        result = agent.invoke({"user_input": user_input})
        print("Agent:", result["final_response"])
