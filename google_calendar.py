import os
import json
import tempfile
from datetime import datetime
import pytz
import base64

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = 'token.json'


def get_calendar_service():
    creds = None

    # Step 1: Try loading cached token
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # Step 2: If not valid, decode creds and run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Using base64 GOOGLE_CREDENTIALS_B64 env var...")

            # Read base64-encoded client secret
            b64_credentials = os.environ.get("GOOGLE_CREDENTIALS_B64")
            if not b64_credentials:
                raise RuntimeError("❌ Missing GOOGLE_CREDENTIALS_B64 environment variable.")

            decoded_json = base64.b64decode(b64_credentials).decode("utf-8")

            # Save decoded credentials to a temp file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp:
                temp.write(decoded_json)
                temp.flush()
                flow = InstalledAppFlow.from_client_secrets_file(temp.name, SCOPES)
                # You CANNOT use flow.run_local_server or run_console on Render
                raise RuntimeError("❌ Cannot launch OAuth in headless environment. Use a pre-generated token.json instead.")

        # Save the fresh token locally
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
    print(f"🕵️ Found {len(events)} event(s) between {start_hour}-{end_hour} on {date}.")
    return len(events) == 0


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
