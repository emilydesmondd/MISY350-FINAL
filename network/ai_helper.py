import json
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from data import json_AI_EMAIL, json_logs


def get_data(json_AI_EMAIL):
    if not json_AI_EMAIL.exists():
        return "[]"
    with open(json_AI_EMAIL, "r", encoding="utf-8") as f:
        data = json.load(f)
        return json.dumps(data, indent=2)


def load_logs(json_logs):
    if json_logs.exists() and json_logs.stat().st_size > 0:
        with open(json_logs, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_logs(json_logs, logs):
    with open(json_logs, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)


def build_ai_prompt(email_context):
    "Builds the hidden instructions and business context for the AI."
    return (
        "You are a helpful networking email assistant.\n"
        "Help students write professional emails, connection requests, follow-ups, and thank-you notes.\n"
        "Use the app context below when it is helpful.\n"
        "If the answer is not in the provided context, still help with general email writing.\n\n"
        f"APP EMAIL CONTEXT:\n{email_context}"
    )


def get_ai_response(client: OpenAI, email_context: str, chat_history: list):
    "Combines hidden instructions with visible chat history, then calls the AI."
    ai_prompt = build_ai_prompt(email_context)
    ai_prompt_message = [{"role": "system", "content": ai_prompt}]
    messages = ai_prompt_message + chat_history
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content


def render_ai_email_helper() -> None:
    st.markdown("### AI Email Helper")

    load_dotenv()
    api_key = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY or API_KEY was not found. Check your .env file.")
        st.stop()

    client = OpenAI(api_key=api_key)
    email_context = get_data(json_AI_EMAIL)

    if "messages" not in st.session_state:
        st.session_state.messages = []
        logs = load_logs(json_logs)
        for log in logs:
            st.session_state.messages.append({"role": "user", "content": log["user_message"]})
            st.session_state.messages.append({"role": "assistant", "content": log["assistant_message"]})

        if len(st.session_state.messages) == 0:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Hi! Ask me for help writing a networking email, follow-up, or thank-you message.",
            })

    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_input = st.chat_input("Type your question...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container.chat_message("user"):
            st.markdown(user_input)

        assistant_response = get_ai_response(client, email_context, st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with chat_container.chat_message("assistant"):
            st.markdown(assistant_response)

        saved_logs = load_logs(json_logs)
        saved_logs.append({
            "user_message": user_input,
            "assistant_message": assistant_response,
        })
        save_logs(json_logs, saved_logs)
