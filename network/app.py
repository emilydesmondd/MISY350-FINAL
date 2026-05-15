import streamlit as st

from ai_helper import render_ai_email_helper
from data import (
    ai_email_context,
    connections,
    json_AI_EMAIL,
    json_connections,
    json_logs,
    json_users,
    load_data,
    logs,
    users
)
from pages import (
    render_advisor_dashboard,
    render_advisor_home,
    render_login,
    render_profile_setup,
    render_signup,
    render_student_dashboard,
    render_student_home,
)
from sidebar import render_sidebar


def initialize_session_state() -> None:
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "page" not in st.session_state:
        st.session_state["page"] = "login"
    if "role" not in st.session_state:
        st.session_state["role"] = None


def main() -> None:
    st.set_page_config(
        page_title="Network Manager",
        page_icon=":globe_with_meridians:",
        layout="wide",
        initial_sidebar_state="collapsed",

    )

    initialize_session_state()

    loaded_users = load_data(json_users, users)
    loaded_connection_requests = load_data(json_connections, connections)
    loaded_ai_email = load_data(json_AI_EMAIL, ai_email_context)
    loaded_logs = load_data(json_logs, logs)


    current_page = st.session_state["page"]
    current_role = st.session_state["role"]

    if current_page == "signup":
        render_signup(loaded_users)
    elif current_page == "profile_setup":
        render_profile_setup(loaded_users)
    elif current_page == "login":
        render_login(loaded_users)
    elif current_role == "Advisor":
        if current_page == "advisor_home_page":
            render_advisor_home(loaded_connection_requests)
        elif current_page == "advisor_dashboard":
            render_advisor_dashboard(loaded_users, loaded_connection_requests)
    elif current_role == "Student":
        if current_page == "student_home_page":
            render_student_home(loaded_users, loaded_connection_requests)
        elif current_page == "student_dashboard":
            render_student_dashboard(loaded_users, loaded_connection_requests)
        elif current_page == "AI_email_helper":
            render_ai_email_helper()

    if st.session_state.get("logged_in", False):
        render_sidebar()


if __name__ == "__main__":
    main()