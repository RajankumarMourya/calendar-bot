
from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from google_calendar import is_time_slot_available, book_meeting

app = FastAPI()

# Allow frontend (Streamlit) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class BookingRequest(BaseModel):
    date: str
    start_hour: int
    end_hour: int
    summary: str = "Meeting via AI Bot"

@app.get("/")
def root():
    return {"message": "API is running."}

@app.get("/check")
def check_availability(date: str = Query(...), start_hour: int = Query(...), end_hour: int = Query(...)):
    available = is_time_slot_available(date, start_hour, end_hour)
    return {"available": available}

@app.post("/book")
def book_time_slot(req: BookingRequest):
    success = book_meeting(req.date, req.start_hour, req.end_hour, req.summary)
    return {"booked": success}
