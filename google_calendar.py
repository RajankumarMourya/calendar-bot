import os
import json
import tempfile
from datetime import datetime
import pytz

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = 'token.json'

def get_calendar_service():
    creds = None

    # 1. Try loading from cached token
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # 2. If no valid credentials, use OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Launching Google OAuth login...")

            # Load credentials from environment variable
            credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
            if not credentials_json:
                raise RuntimeError("Missing GOOGLE_CREDENTIALS_JSON env variable.")

            # Save to a temp file for OAuth
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
                temp.write(credentials_json.encode())
                temp.flush()
                flow = InstalledAppFlow.from_client_secrets_file(temp.name, SCOPES)
                creds = flow.run_local_server(port=0)

        # Save token for reuse
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

# Check if time slot is available
def is_time_slot_available(date: str, start_hour: int, end_hour: int) -> bool:
    service = get_calendar_service()
    ist = pytz.timezone("Asia/Kolkata")

    start_time = ist.localize(datetime.strptime(f"{date} {start_hour}", "%Y-%m-%d %H"))
    end_time = ist.localize(datetime.strptime(f"{date} {end_hour}", "%Y-%m-%d %H"))

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    print(f"🕵️ Found {len(events)} event(s) between {start_hour}-{end_hour} on {date}.")
    return len(events) == 0

# Book the meeting
def book_meeting(date: str, start_hour: int, end_hour: int, summary: str) -> bool:
    service = get_calendar_service()
    ist = pytz.timezone("Asia/Kolkata")

    start_time = ist.localize(datetime.strptime(f"{date} {start_hour}", "%Y-%m-%d %H"))
    end_time = ist.localize(datetime.strptime(f"{date} {end_hour}", "%Y-%m-%d %H"))

    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'}
    }

    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print("✅ Event created:", created_event.get('htmlLink'))
        return True
    except Exception as e:
        print("❌ Failed to book event:", e)
        return False
