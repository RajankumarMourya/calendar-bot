import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = 'token.json'
CREDS_PATH = 'credentials.json'


def get_calendar_service():
    creds = None

    # Check if token.json exists (cached credentials)
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # If no (valid) credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Launching browser for Google login...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the token for future use
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


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
    print(f"🕵️ Found {len(events)} event(s) from {start_time} to {end_time}")
    return len(events) == 0



def book_meeting(date: str, start_hour: int, end_hour: int, summary: str) -> bool:
    service = get_calendar_service()

    start_time = datetime.strptime(f"{date} {start_hour}", "%Y-%m-%d %H")
    end_time = datetime.strptime(f"{date} {end_hour}", "%Y-%m-%d %H")

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
