
import uuid
import streamlit as st

from datetime import datetime
from components.query_window import render_chat
from components.voice_assistant import render_voice_input, render_voice_status, speak_text
from components.chat_handler import add_user_message, add_agent_placeholder, fetch_response, update_last_agent_message, save_history


# MAIN CHATBOT

def render_chatbot():

    # Session State

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "AI Assistant"

    if "voice_mode" not in st.session_state:
        st.session_state.voice_mode = False

    if "last_agent_reply" not in st.session_state:
        st.session_state.last_agent_reply = ""

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    # Tabs

    tab1, tab2 = st.columns(2)

    with tab1:

        if st.button(
            "✨ AI Assistant",
            use_container_width=True,
            type="primary"
            if st.session_state.active_tab == "AI Assistant"
            else "secondary",
        ):
            st.session_state.active_tab = "AI Assistant"
            st.rerun()

    with tab2:

        if st.button(
            "⏱️ Query History",
            use_container_width=True,
            type="primary"
            if st.session_state.active_tab == "Query History"
            else "secondary",
        ):
            st.session_state.active_tab = "Query History"
            st.rerun()

    st.divider()

    # AI ASSISTANT

    if st.session_state.active_tab == "AI Assistant":

        left, right = st.columns([3, 1])

        with left:

            st.markdown(
                """
                ###  Hello! I'm EcomAI

                I'm your **E-Commerce Operations Agent**.
                """
            )

        with right:

            voice_label = (
                "🔇 Voice"
                if st.session_state.voice_mode
                else "🔊 Voice"
            )

            if st.button(
                voice_label,
                use_container_width=True,
            ):
                st.session_state.voice_mode = (
                    not st.session_state.voice_mode
                )
                st.rerun()

        # Quick Actions

        quick_actions = [
            (
                "🔮 Find delayed orders",
                "Find delayed orders and escalate critical ones.",
            ),
            (
                "📄 Generate weekly report",
                "Generate weekly operations report.",
            ),
        ]

        for title, prompt in quick_actions:

            if st.button(
                title,
                use_container_width=True,
            ):
                _handle_new_message(prompt)

        st.divider()

        if st.session_state.voice_mode:
            render_voice_status(False)

        # Chat Window

        if st.session_state.chat_messages:
            render_chat(
                st.session_state.chat_messages,
                height=450,
            )
        else:
            st.info("👋 Start a conversation by typing a message below.")

        # If last message is loading,
        # call backend and replace loading bubble

        if (
            len(st.session_state.chat_messages)
            and st.session_state.chat_messages[-1].get("loading", False)
        ):

            user_query = st.session_state.chat_messages[-2]["msg"]

            agent_reply = fetch_response(
                user_query,
                st.session_state.session_id,
            )

            update_last_agent_message(agent_reply)

            st.session_state.last_agent_reply = agent_reply

            save_history(user_query)

            st.rerun()

        # Workflow Status

        st.markdown(
            """
            <div style="
                background:#0f172a;
                border:1px solid #1e293b;
                border-radius:10px;
                padding:12px;
                margin-top:10px;
                margin-bottom:15px;
            ">

            <div style="
                color:#94a3b8;
                font-size:11px;
                font-weight:bold;
                margin-bottom:8px;
            ">
            ⚙️ WORKFLOW STATUS
            </div>

            <div style="font-size:12px;">

            <div style="display:flex;justify-content:space-between;">
            <span>🟢 Planner Agent</span>
            <span style="color:#10b981;">Completed</span>
            </div>

            <div style="display:flex;justify-content:space-between;">
            <span>🟢 Database Agent</span>
            <span style="color:#10b981;">Completed</span>
            </div>

            <div style="display:flex;justify-content:space-between;">
            <span>🟢 Policy Agent</span>
            <span style="color:#10b981;">Completed</span>
            </div>

            <div style="display:flex;justify-content:space-between;">
            <span>🟢 Report Agent</span>
            <span style="color:#10b981;">Completed</span>
            </div>

            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # Speak response

        if (
            st.session_state.voice_mode
            and st.session_state.last_agent_reply
        ):

            speak_text(st.session_state.last_agent_reply)

            st.session_state.last_agent_reply = ""

        # Input

        st.caption("TYPE or USE VOICE")

        with st.form(
            "chat_input",
            clear_on_submit=True,
        ):

            user_query = st.text_input(
                "",
                placeholder="Type a message...",
                label_visibility="collapsed",
            )

            send = st.form_submit_button(
                "Send",
                use_container_width=True,
                type="primary",
            )

            if send and user_query.strip():

                _handle_new_message(user_query)

        # Voice Input

        if st.session_state.voice_mode:

            spoken = render_voice_input()

            if spoken:

                st.success(f"🎤 {spoken}")

                _handle_new_message(spoken)

    # QUERY HISTORY
    else:

        st.caption("Previously executed queries")

        if not st.session_state.query_history:
            st.info("No previous queries.")
        else:

            for item in st.session_state.query_history:

                st.markdown(
                    f"""
                    <div style="
                        background:#111827;
                        border:1px solid #1f2937;
                        border-radius:8px;
                        padding:12px;
                        margin-bottom:8px;
                    ">
                        <b>{item['title']}</b><br>
                        <small style="color:gray;">
                        {item['date']}
                        </small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# Handle New Message

def _handle_new_message(user_text: str):
    """ Adds the user message and a loading bubble.The actual API call is performed during the next render
    so the typing animation is visible."""

    add_user_message(user_text)

    add_agent_placeholder()

    st.rerun()