import streamlit as st
import requests
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

st.set_page_config(page_title="TailorTalk", page_icon="🧵")
st.title("🧵 TailorTalk Booking Agent")

# Load Google credentials from Streamlit secrets
def get_calendar_service():
    try:
        creds_data = json.loads(st.secrets["google"]["token"])
        creds = Credentials.from_authorized_user_info(creds_data)
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        st.error(f"❌ Failed to load credentials: {e}")
        st.stop()

# Store messages in session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("What would you like to do?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("🤖 Thinking..."):
        try:
            response = requests.post(
                "https://tailor-talk-fastapi.onrender.com/chat",  # ✅ Update this to your real FastAPI endpoint if hosted
                json={"message": prompt},
                timeout=60
            )
            response.raise_for_status()
            reply = response.json()["response"]
        except Exception as e:
            reply = f"❌ Something went wrong: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
