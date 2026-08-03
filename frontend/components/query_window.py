import streamlit as st


def render_chat(messages, height=500):
    

    st.markdown("""
    <style>

    div[data-testid="stChatMessage"]{
        margin-bottom:12px;
    }

    div[data-testid="stChatMessageContent"]{
        border-radius:12px;
        padding:12px;
        font-size:13px;
        line-height:1.5;
    }

    .typing{
        display:flex;
        align-items:center;
        gap:5px;
        padding:6px 0;
    }

    .typing span{
        width:8px;
        height:8px;
        border-radius:50%;
        background:#60A5FA;
        animation:typing 1.4s infinite ease-in-out;
    }

    .typing span:nth-child(2){
        animation-delay:.2s;
    }

    .typing span:nth-child(3){
        animation-delay:.4s;
    }

    @keyframes typing{
        0%,80%,100%{
            transform:scale(.4);
            opacity:.5;
        }

        40%{
            transform:scale(1);
            opacity:1;
        }
    }

    </style>
    """, unsafe_allow_html=True)

    chat_container = st.container(height=height)

    with chat_container:

        for msg in messages:

            avatar = "👤" if msg["role"] == "User" else "🤖"

            with st.chat_message(
                "user" if msg["role"] == "User" else "assistant",
                avatar=avatar
            ):

                if msg.get("time"):
                    st.caption(msg["time"])

                # ---------- Typing Bubble ----------
                if msg.get("loading", False):

                    st.markdown("""
                    <div class="typing">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>

                    <div style="
                        font-size:12px;
                        color:#9ca3af;
                        margin-top:4px;
                    ">
                    EcomAI is thinking...
                    </div>
                    """, unsafe_allow_html=True)

                # ---------- Normal Message ----------
                else:
                    st.markdown(msg["msg"])

    # Auto scroll to bottom
    st.markdown("""
    <script>
    const parent=document.querySelector('[data-testid="stVerticalBlock"]');

    if(parent){
        parent.scrollTop=parent.scrollHeight;
    }
    </script>
    """, unsafe_allow_html=True)