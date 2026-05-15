import time

import streamlit as st


def render_sidebar() -> None:
    if not st.session_state.get("logged_in", False):
        return

    with st.sidebar:
        st.markdown(
    "<h1 style='text-align: center;'>Pages</h1>",
    unsafe_allow_html=True

        )
        st. divider()

        if st.session_state["role"] == "Student":
            if st.button("Home ⌂", key="home_btn", type= "secondary", use_container_width=True):
                st.session_state["page"] = "student_home_page"
                st.rerun()
            if st.button("Dashboard 🗂️", key="dash_btn", type= "secondary", use_container_width=True):
                st.session_state["page"] = "student_dashboard"
                st.rerun()
            if st.button("AI Email Helper ֎", key="ai_btn", type= "secondary", use_container_width=True):
                st.session_state["page"] = "AI_email_helper"
                st.rerun()
            if st.button("Profile 👤", key="profile_btn", type= "secondary", use_container_width=True):
                st.session_state["page"] = "profile_setup"
                st.rerun()

            st.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
            if st.button("Logout ➜]", key="logout_btn", type= "tertiary", use_container_width=True):
                with st.spinner("logging out..."):
                    time.sleep(2)
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["page"] = "login"
                st.rerun()

        if st.session_state["role"] == "Advisor":
            if st.button("Home ⌂", key="home_btn_2", type= "secondary", use_container_width=True):
                st.session_state["page"] = "advisor_home_page"
                st.rerun()
            if st.button("Dashboard 🗂️", key="dash_btn_2", type= "secondary", use_container_width=True):
                st.session_state["page"] = "advisor_dashboard"
                st.rerun()

            st.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
            if st.button("Logout ➜]", key="logout_btn_2", type= "tertiary", use_container_width=True):
                with st.spinner("logging out..."):
                    time.sleep(2)
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["page"] = "login"
                st.rerun()
