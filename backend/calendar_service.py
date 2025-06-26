import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_calendar_service():
    creds = Credentials.from_authorized_user_file("backend/token.json")
    return build("calendar", "v3", credentials=creds)

def check_slot_availability(service, calendar_id, start_time, end_time):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    return len(events) == 0  # True if slot is free
