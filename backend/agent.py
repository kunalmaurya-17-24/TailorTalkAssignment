import json
import copy
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from langgraph.graph import StateGraph, END
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load secrets from .env
load_dotenv()
CALENDAR_ID = os.getenv("CALENDAR_ID")
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize HF client
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=HF_TOKEN
)

intent_prompt = """You are a JSON-generating AI. Given the user's input, return only a single valid JSON object with:
- "intent": one of ["book_slot", "suggest_slots", "reschedule_slot", "cancel_slot"]
- "date_time": ISO format "YYYY-MM-DDTHH:MM:SS" or null
- "duration": integer in minutes, default to 30

ONLY return valid JSON. No explanation or extra text.
Example:
```json
{
  "intent": "book_slot",
  "date_time": "2025-06-27T12:00:00",
  "duration": 30
}
```"""

@dataclass
class AgentState:
    messages: list
    intent: str = "suggest_slots"
    date_time: datetime = None
    duration: int = 30
    availability: list = None
    booking_status: str = None
    suggested_time: datetime = None

def call_hf(prompt: str) -> str:
    try:
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print("❌ HF API error:", e)
        return ""

# ✅ Render-safe credentials loader
def get_calendar_service():
    try:
        creds = Credentials.from_authorized_user_file("token.json")
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        print("❌ Failed to load calendar credentials:", e)
        return None

def detect_intent(state: AgentState):
    user_input = state.messages[-1].strip()
    prompt = intent_prompt + f'\nUser input: "{user_input}"\n```json'
    response = call_hf(prompt)

    parsed = {"intent": "suggest_slots", "date_time": None, "duration": 30}
    if response.strip():
        try:
            match = re.search(r"\{[\s\S]*?\}", response)
            if match:
                parsed = json.loads(match.group(0))
        except Exception:
            print("⚠️ Could not parse JSON. Raw output:", repr(response))

    new_state = copy.deepcopy(state)
    new_state.intent = parsed.get("intent", "suggest_slots")
    dt_str = parsed.get("date_time")

    if dt_str:
        try:
            new_state.date_time = datetime.fromisoformat(dt_str).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        except Exception:
            pass
    elif "tomorrow afternoon" in user_input.lower():
    now_ist = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    new_state.date_time = (now_ist + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
    new_state.intent = "book_slot"


    new_state.duration = parsed.get("duration", 30)
    return new_state

def check_availability(state: AgentState):
    new_state = copy.deepcopy(state)
    if not state.date_time or state.intent != "book_slot":
        new_state.availability = ["Please specify a date and time."]
        return new_state

    try:
        service = get_calendar_service()
        if not service:
            raise Exception("Google Calendar service not initialized")

        start = state.date_time.isoformat()
        end = (state.date_time + timedelta(minutes=state.duration)).isoformat()

        events = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start,
            timeMax=end,
            maxResults=5,
            singleEvents=True
        ).execute().get("items", [])

        if not events:
            new_state.availability = ["Available"]
        else:
            new_state.availability = ["Not available"]
            suggested = state.date_time + timedelta(minutes=30)
            while True:
                sug_start = suggested.isoformat()
                sug_end = (suggested + timedelta(minutes=state.duration)).isoformat()
                res = service.events().list(
                    calendarId=CALENDAR_ID,
                    timeMin=sug_start,
                    timeMax=sug_end,
                    maxResults=1,
                    singleEvents=True
                ).execute()
                if not res.get("items", []):
                    new_state.suggested_time = suggested
                    break
                suggested += timedelta(minutes=30)

    except HttpError as e:
        new_state.availability = [f"Error checking availability: {e}"]
    except Exception as e:
        new_state.availability = [f"Internal error: {e}"]

    return new_state

def book_slot(state: AgentState):
    new_state = copy.deepcopy(state)
    service = get_calendar_service()
    if not service:
        new_state.booking_status = "❌ Google Calendar credentials error"
        return new_state

    event = {
        "summary": "TailorTalk Call",
        "start": {"dateTime": state.date_time.isoformat(), "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": (state.date_time + timedelta(minutes=state.duration)).isoformat(), "timeZone": "Asia/Kolkata"},
        "description": f"Scheduled TailorTalk call for {state.duration} minutes.",
        "conferenceData": {
            "createRequest": {
                "requestId": f"tailortalk-{int(datetime.now().timestamp())}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"}
            }
        }
    }

    try:
        created = service.events().insert(
            calendarId=CALENDAR_ID,
            body=event,
            conferenceDataVersion=1
        ).execute()
        meet_link = created.get("hangoutLink", "")
        new_state.booking_status = f"Booked. Meet link: {meet_link}"
    except HttpError as e:
        new_state.booking_status = f"Failed: {e}"
    return new_state

def send_confirmation(state: AgentState):
    new_state = copy.deepcopy(state)
    if state.booking_status and "Booked" in state.booking_status:
        when = state.date_time.strftime("%A, %B %d at %I:%M %p IST")
        new_state.messages.append(
            f"✅ Your call is scheduled on {when} for {state.duration} minutes.\n{state.booking_status}"
        )
    else:
        msg = f"❌ Booking failed: {state.booking_status}"
        if state.suggested_time:
            msg += f"\n💡 Suggested: {state.suggested_time.strftime('%A at %I:%M %p')}"
        new_state.messages.append(msg)
    return new_state

# LangGraph pipeline
workflow = StateGraph(AgentState)
workflow.add_node("detect_intent", detect_intent)
workflow.add_node("check_availability", check_availability)
workflow.add_node("book_slot", book_slot)
workflow.add_node("send_confirmation", send_confirmation)

workflow.set_entry_point("detect_intent")
workflow.add_edge("detect_intent", "check_availability")
workflow.add_conditional_edges(
    "check_availability",
    lambda s: "book_slot" if s.availability and "Available" in s.availability else "send_confirmation"
)
workflow.add_edge("book_slot", "send_confirmation")
workflow.add_edge("send_confirmation", END)

agent = workflow.compile()

def run_agent(message: str):
    try:
        initial_state = AgentState(messages=[message])
        final_state = agent.invoke(initial_state)

        # Return last message as reply
        if hasattr(final_state, "messages"):
            return final_state.messages[-1]
        elif isinstance(final_state, dict):
            return final_state.get("messages", ["❌ No message returned"])[-1]
        else:
            return "❌ Unexpected agent response structure"
    except Exception as e:
        print("❌ Error in run_agent:", e)
        return f"❌ Something went wrong: {e}"
