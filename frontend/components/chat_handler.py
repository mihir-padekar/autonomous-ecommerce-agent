from datetime import datetime
import streamlit as st
from services.api_client import APIClient


def add_user_message(user_text: str):
    """
    Adds only the user message.
    """

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    now = datetime.now().strftime("%I:%M %p")

    st.session_state.chat_messages.append({
        "role": "User",
        "time": now,
        "msg": user_text
    })


def add_agent_placeholder():
    """
    Adds an empty assistant message.
    """

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    st.session_state.chat_messages.append({
        "role": "Agent",
        "time": "",
        "msg": "",
        "loading": True
    })


def fetch_response(query: str, session_id: str):

    result = APIClient.send_chat_query(
        query,
        session_id
    )

    if result.get("error"):
        return f"❌ Backend Error\n\n{result['message']}"

    if result.get("chat_response"):
        return result["chat_response"]

    if result.get("report"):
        return result["report"]

    return "⚠️ No response received from backend."


def update_last_agent_message(reply: str):
    """
    Replace loading bubble with real response.
    """

    now = datetime.now().strftime("%I:%M %p")

    st.session_state.chat_messages[-1] = {
        "role": "Agent",
        "time": now,
        "msg": reply,
        "loading": False
    }

    st.session_state.last_agent_reply = reply


def save_history(query: str):

    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    st.session_state.query_history.insert(0, {
        "title": f"🔍 {query[:45]}{'...' if len(query) > 45 else ''}",
        "date": "Just Now"
    })