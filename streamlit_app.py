import streamlit as st
import json
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from huggingface_hub import InferenceClient
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

# Load secrets
CALENDAR_ID = st.secrets["CALENDAR_ID"]
HF_TOKEN = st.secrets["HF_TOKEN"]
GOOGLE_CREDS = json.loads(st.secrets["google"]["credentials"])

# Setup Hugging Face model
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=HF_TOKEN
)

intent_prompt = """You are a JSON-generating AI. Given the user's input, return only a single valid JSON object with:
- "intent": one of ["book_slot", "suggest_slots"]
- "date_time": ISO format "YYYY-MM-DDTHH:MM:SS" or null
- "duration": integer in minutes, default to 30

ONLY return valid JSON. No explanation or extra text.
Example:
```json
{
  "intent": "book_slot",
  "date_time": "2025-06-28T15:00:00",
  "duration": 30
}
```"""

def call_hf(prompt: str) -> str:
    try:
        print("🔁 Sending chat completion request...")
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print("❌ HF Error:", e)
        return ""

def get_calendar_service():
    creds = InstalledAppFlow.from_client_config(
        GOOGLE_CREDS,
        scopes=["https://www.googleapis.com/auth/calendar"]
    ).run_local_server(port=0)
    return build("calendar", "v3", credentials=creds)

def parse_user_input(user_input):
    prompt = intent_prompt + f'\nUser input: "{user_input}"\n```json'
    response = call_hf(prompt)

    parsed = {"intent": "suggest_slots", "date_time": None, "duration": 30}
    try:
        match = re.search(r"\{[\s\S]*?\}", response)
        if match:
            parsed = json.loads(match.group(0))
    except Exception as e:
        print("⚠️ JSON parsing failed:", e)

    dt = parsed.get("date_time")
    if dt:
        try:
            dt = datetime.fromisoformat(dt).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        except:
            dt = None
    elif "tomorrow afternoon" in user_input.lower():
        dt = (datetime.now(tz=ZoneInfo("Asia/Kolkata")) + timedelta(days=1)).replace(hour=12, minute=0)
        parsed["intent"] = "book_slot"

    parsed["date_time"] = dt
    return parsed

def book_slot(date_time, duration):
    service = get_calendar_service()
    start = date_time.isoformat()
    end = (date_time + timedelta(minutes=duration)).isoformat()

    try:
        events = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start,
            timeMax=end,
            maxResults=1,
            singleEvents=True
        ).execute().get("items", [])
        if events:
            return None, "❌ Slot not available."

        event = {
            "summary": "TailorTalk Call",
            "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end, "timeZone": "Asia/Kolkata"},
            "description": f"Auto-booked via TailorTalk for {duration} minutes.",
            "conferenceData": {
                "createRequest": {
                    "requestId": f"tailortalk-{int(datetime.now().timestamp())}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            }
        }

        created = service.events().insert(
            calendarId=CALENDAR_ID,
            body=event,
            conferenceDataVersion=1
        ).execute()

        meet_link = created.get("hangoutLink", "No link available.")
        when = date_time.strftime("%A, %B %d at %I:%M %p IST")
        return f"✅ Your call is booked for {when}.\n🔗 Meet Link: {meet_link}", None

    except HttpError as e:
        return None, f"❌ Booking failed: {e}"

# 🟩 Streamlit UI
st.set_page_config(page_title="TailorTalk", page_icon="🧵")
st.title("🧵 TailorTalk Booking Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if user_input := st.chat_input("What would you like to do?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("🤖 Thinking..."):
        result = parse_user_input(user_input)
        if result["intent"] == "book_slot" and result["date_time"]:
            reply, error = book_slot(result["date_time"], result["duration"])
        else:
            reply = "🤔 Please provide a valid date and time to book."
            error = None

    if error:
        reply = error

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
