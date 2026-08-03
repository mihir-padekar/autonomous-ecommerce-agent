import streamlit as st
from contextlib import contextmanager


@contextmanager
def loading(message="Loading..."):

    placeholder = st.empty()

    placeholder.markdown(
            f"""
            <style>
            .loader-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(15,23,42,0.92);
                display:flex;
                justify-content:center;
                align-items:center;
                z-index:999999;
            }}

            .loader-content {{
                display:flex;
                flex-direction:column;
                align-items:center;
            }}

            .loader {{
                width:90px;
                height:90px;
                border:8px solid #374151;
                border-top:8px solid #6366F1;
                border-radius:50%;
                animation:spin 1s linear infinite;
            }}

            .loader-text {{
                margin-top:20px;
                color:white;
                font-size:22px;
                font-weight:600;
            }}

            @keyframes spin {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
            </style>

            <div class="loader-overlay">
                <div class="loader-content">
                    <div class="loader"></div>
                    <div class="loader-text">{message}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    try:
        yield
    finally:
        placeholder.empty()
