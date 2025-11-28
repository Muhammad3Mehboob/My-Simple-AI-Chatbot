
import streamlit as st
from dotenv import load_dotenv
from google import genai
import os
from datetime import datetime

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

st.title("Basic AI Chatbot")

# Persona selector
PERSONA_MAP = {
    "Technical Instructor": "You are a professional Python and Streamlit tutor. Explain concepts clearly and simply.",
    "Friendly Robot": "You are a friendly, upbeat conversational robot.",
    "Sarcastic Critic": "You are a cynical, slightly rude AI assistant."
}

selected_persona = st.sidebar.selectbox(
    "Select Chatbot Personality:",
    options=list(PERSONA_MAP.keys()),
    key="current_persona"
)

persona_instruction = PERSONA_MAP[selected_persona]

# Reset chat if persona changes
if "last_persona" not in st.session_state:
    st.session_state.last_persona = selected_persona

if selected_persona != st.session_state.last_persona:
    st.session_state.messages = []
    if "gemini_chat" in st.session_state:
        del st.session_state["gemini_chat"]
    st.session_state.last_persona = selected_persona

# Create history list
if "messages" not in st.session_state:
    st.session_state.messages = []

# BUBBLE STYLE FUNCTION WITH TIMESTAMP
def render_bubble(role, text, timestamp):
    if role == "user":
        bubble_color = "#E0F3FF"   # light blue
        prefix = "👤 **You**"
    else:
        bubble_color = "#F5F5F5"   # light grey
        prefix = "🤖 **Bot**"

    st.markdown(
        f"""
        <div style="
            background:{bubble_color};
            padding:12px;
            border-radius:12px;
            margin-bottom:10px;
            width:fit-content;
            max-width:80%;
        ">
            {prefix} <span style="font-size:11px;color:gray;">({timestamp})</span><br>
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        render_bubble(message["role"], message["content"], message["time"])

# User input
if prompt := st.chat_input("Enter your message here..."):

    current_time = datetime.now().strftime("%H:%M:%S")

    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": current_time
    })

    with st.chat_message("user"):
        render_bubble("user", prompt, current_time)

    # Initialize chat if not present
    if "gemini_chat" not in st.session_state:
        st.session_state.gemini_chat = client.chats.create(
            model="gemini-2.5-flash",
            config={"system_instruction": persona_instruction}
        )

    gemini_chat = st.session_state.gemini_chat

    # Get model response
    response = gemini_chat.send_message(prompt)
    reply = response.text

    bot_time = datetime.now().strftime("%H:%M:%S")

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "time": bot_time
    })

    with st.chat_message("assistant"):
        render_bubble("assistant", reply, bot_time)

# Clear history button
def clear_chat_history():
    st.session_state.messages = []
    if "gemini_chat" in st.session_state:
        del st.session_state["gemini_chat"]

st.sidebar.button("Clear History", on_click=clear_chat_history)
