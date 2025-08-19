import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
# import os
# api_key = os.getenv("GROQ_API_KEY")
# -------------------------
# Page title
# -------------------------
st.set_page_config(page_title="Chatgpt", layout="wide")
st.title("💬 Chatgpt")

# -------------------------
# Initialize session state
# -------------------------
if "client" not in st.session_state:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ Missing GROQ_API_KEY environment variable")
        st.stop()
    st.session_state["client"] = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# -------------------------
# Sidebar parameters
# -------------------------
st.sidebar.title("⚙️ Model Parameters")
temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
max_tokens = st.sidebar.slider("Max Tokens", 1, 4096, 512)

# -------------------------
# Display conversation history
# -------------------------
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------
# Chat input
# -------------------------
if prompt := st.chat_input("Enter your query..."):
    # Save user message
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant streaming response
    with st.chat_message("assistant"):
        client = st.session_state["client"]

        # Create placeholder for streaming response
        placeholder = st.empty()
        full_response = ""

        stream = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state["messages"]
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        # Stream tokens as they arrive
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                full_response += delta.content
                placeholder.markdown(full_response + "▌")  # show typing cursor

        # Final response without cursor
        placeholder.markdown(full_response)

    # Save assistant response to history
    st.session_state["messages"].append({"role": "assistant", "content": full_response})

# st.write("📦 Session State:", st.session_state)