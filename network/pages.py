import time
import os
import streamlit as st

from auth import authenticate_user, create_account, update_profile
from connections import add_connection_request, find_advisor_by_label, get_advisor_options
from data import json_connections, json_users, logs, save_data
from data import save_resume


def render_signup(users: list) -> None:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
    "<h1 style='text-align: center;'>Network Manager 🌐</h1>",
    unsafe_allow_html=True
)

    st.divider()

    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:
        st.markdown(
    "<h2 style='text-align: center;'>Create an Account!</h2>",
    unsafe_allow_html=True)

        with st.container(border=True):
            full_name_signup = st.text_input("Full Name", key="full_name_signup", placeholder="John Doe")
            email_signup = st.text_input("Email Address", key="email_signup", placeholder="john.doe@udel.edu")
            password_signup = st.text_input(
                "Password",
                type="password",
                key="password_signup",
                placeholder="Create a strong password",
            )
            role_signup = st.selectbox("Role", ["Student", "Advisor"], key="role_signup")

            if st.button("Create Account", type="primary", use_container_width=True):
                if not full_name_signup or not email_signup or not password_signup:
                    st.warning("Please fill out all fields.")
                else:
                    new_user = create_account(users, full_name_signup, email_signup, password_signup, role_signup)

                    if new_user is None:
                        st.error("An account with this email already exists.")
                    else:
                        save_data(users, json_users)
                        st.session_state["logged_in"] = False
                        st.session_state["user"] = new_user
                        st.session_state["role"] = role_signup

                        with st.spinner("Creating account..."):
                            time.sleep(2)

                        st.success(f"Account created! Welcome, {full_name_signup}!")
                        st.session_state["page"] = "login"
                        st.rerun()

            if st.button("Have an Account? Log In", type="secondary", use_container_width=True):
                st.session_state["page"] = "login"
                st.rerun()


def render_profile_setup(users: list) -> None:
    if st.session_state["user"] is None:
        st.warning("Please log in first.")
        st.session_state["page"] = "login"
        st.rerun()
    left_spacer, center_column, right_spacer = st.columns([1, 3, 1])
    with center_column:

        st.markdown(
    "<h1 style='text-align: center;'>Profile Setup</h1>",
    unsafe_allow_html=True)
        
        st.divider()

        with st.container(border=True):
                profile_full_name = st.text_input(
                    "Student Name",
                    value=st.session_state["user"].get("full_name", ""),
                    key="profile_full_name",
                )
                profile_email = st.text_input(
                    "Student Email",
                    value=st.session_state["user"].get("email", ""),
                    key="profile_email",
                )
                profile_school = st.text_input(
                    "School",
                    value=st.session_state["user"].get("school", ""),
                    key="profile_school",
                )
                profile_major = st.text_input(
                    "Major",
                    value=st.session_state["user"].get("major", ""),
                    key="profile_major",
                )

        if st.button("Save Profile", type="primary", use_container_width=True):
                updated_user = update_profile(
                    users,
                    st.session_state["user"].get("email", ""),
                    profile_full_name,
                    profile_email,
                    profile_school,
                    profile_major,
                )

                if updated_user is not None:
                    save_data(users, json_users)
                    st.session_state["user"] = updated_user

                with st.spinner("Saving profile..."):
                    time.sleep(3)
                    st.success("Profile setup complete!")
                    time.sleep(2)
                    st.rerun()


def render_login(users: list) -> None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
    "<h1 style='text-align: center;'>Network Manager 🌐</h1>",
    unsafe_allow_html=True
)

    st.divider()

    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:
        st.markdown(
    "<h2 style='text-align: center;'>Log In</h2>",
    unsafe_allow_html=True
)

        with st.container(border=True):
            email_input = st.text_input("Email Address", key="email_login", placeholder="Enter your email")
            password_input = st.text_input(
                "Password",
                type="password",
                key="password",
                placeholder="Enter your password",
            )

            if st.button("Log In", type="primary", use_container_width=True):
                with st.spinner("Logging in..."):
                    time.sleep(2)

                found_user = authenticate_user(users, email_input, password_input)
                if found_user:
                    st.success(f"Welcome back, {found_user['email']}!")
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = found_user
                    st.session_state["role"] = found_user["role"]
                    if found_user["role"] == "Student":
                        st.session_state["page"] = "student_home_page"
                    else:
                        st.session_state["page"] = "advisor_home_page"
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")

            if st.button("Don't have an account? Sign Up", type="secondary", use_container_width=True):
                st.session_state["page"] = "signup"
                st.rerun()


def render_advisor_home(connection_requests: list) -> None:
    st.header(f"Welcome, {st.session_state['user']['full_name']}!")
    st.subheader("Your Network")

    user_email = st.session_state["user"]["email"].strip().lower()

    user_connections = [
    req for req in connection_requests
    if req.get("advisor_email","").strip().lower() == user_email]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.metric("Total Connections", len(user_connections))

    with col2:
        with st.container(border=True):
            st.metric(
                "Pending Requests",
                len([req for req in user_connections if req.get("status","").lower() == "pending"])
            )

    with col3:
        with st.container(border=True):
            st.metric(
                "Connections",
                len([req for req in user_connections if req.get("status","").lower() == "approved"])
            )

    with col4:
        with st.container(border=True):
            st.metric("Emails", len(logs))


    left, right = st.columns([2, 1])
    with left:
        with st.container(border=True):
            user_email = st.session_state["user"]["email"].strip().lower()

            user_connections = [
                conn for conn in connection_requests
                if conn.get("advisor_email", "").strip().lower() == user_email
            ]

            if user_connections:
                st.subheader("Recent Connections")

                recent_connections = user_connections[-7:]

                for conn in recent_connections:
                    with st.container(border=True):
                        col1, col2 = st.columns([3,1])

                        with col1:
                            st.markdown(
                                f"**{conn.get('student_name', '')}**  \n"
                                f"{conn.get('student_school', '')}"
                            )

                        with col2:
                            status = conn.get('status', '')

                            if status == "Approved":
                                st.success(status)
                            elif status == "Pending":
                                st.warning(status)
                            elif status == "Rejected":
                                st.error(status)
                            else:
                                st.info(status)
            else:
                st.info("No connections yet. Start by accepting requests!")
    with right:
        with st.container(border=True):
            st.subheader("Your Details")
            st.write(f"**Name:** {st.session_state['user']['full_name']}")
            st.write(f"**Email:** {st.session_state['user']['email']}")
            st.write(f"**Company:** {st.session_state['user'].get('company', 'Not Provided')}")
            st.write(f"**Position:** {st.session_state['user'].get('position', 'Not Provided')}")

        with st.container(border=True):
            st.subheader("About")
            st.caption(st.session_state["user"].get("about", "No bio available."))


        with st.container(border=True):
            st.subheader("Quick Actions")

            if st.button("➕ Accept Connection", use_container_width=True):
                st.session_state.page = "advisor_dashboard"
            if st.button("👥 View All Connections", use_container_width=True):
                st.session_state.page = "advisor_dashboard"


def render_advisor_dashboard(users: list, connection_requests: list) -> None:
    st.markdown("### Connect with Students!")
    tab1, tab2 = st.tabs(["Students", "Manage Connections"])

    with tab1:
        left_spacer, center_column, right_spacer = st.columns([1, 4, 1])
        with center_column:
            st.header("Student Connection Requests")
            st.markdown("This is where advisors can review student connection requests.")

            advisor_email = st.session_state["user"]["email"].strip().lower()
            view_connections = [
                request
                for request in connection_requests
                if request.get("advisor_email", "").strip().lower() == advisor_email
            ]

            col1, col2, col3 = st.columns([3, 1.5, 1.5])
            with col1:
                st.markdown("## Submitted Requests")
            with col2:
                with st.container(border=True):
                    st.markdown("Count")
                    st.markdown(f"### {len(view_connections)}")
            with col3:
                with st.container(border=True):
                    pending_count = sum(
                        1 for request in view_connections if request.get("status", "").strip().lower() == "pending"
                    )
                    st.markdown("Pending")
                    st.markdown(f"### {pending_count}")

            st.divider()

            with st.container(border=True):
                filter_col1, filter_col2 = st.columns([4, 2])
                with filter_col1:
                    search_item = st.text_input("Search by Student Email", key="search_txt_by_email")
                with filter_col2:
                    selected_status = st.selectbox(
                        "Status",
                        ["All", "Pending", "Approved", "Rejected"],
                        key="selected_status_filter",
                    )

            filtered_requests = view_connections.copy()

            if search_item:
                filtered_requests = [
                    request
                    for request in filtered_requests
                    if search_item.lower() in request.get("student_email", "").lower()
                ]

            if selected_status != "All":
                filtered_requests = [
                    request
                    for request in filtered_requests
                    if request.get("status", "").strip().lower() == selected_status.lower()
                ]

            display_requests = [
                {
                    "Status": request.get("status", ""),
                    "Student Name": request.get("student_name", ""),
                    "Student Email": request.get("student_email", ""),
                    "School": request.get("student_school", ""),
                    "Major": request.get("student_major", ""),
                }
                for request in filtered_requests
            ]

            data_col, details_col = st.columns([4, 2])
            selected_request = None

            with data_col:
                event = st.dataframe(
                    display_requests,
                    on_select="rerun",
                    selection_mode="single-row",
                    use_container_width=True,
                    key="advisor_requests_table",
                )
                if event.selection.rows:
                    selected_index = event.selection.rows[0]
                    selected_request = filtered_requests[selected_index]

            with details_col:
                with st.container(border=True):
                    st.markdown("### Request Details")

                    if selected_request is not None:
                        st.markdown(f"**Status:** {selected_request.get('status', '')}")
                        st.markdown(f"**Student Name:** {selected_request.get('student_name', '')}")
                        st.markdown(f"**Student Email:** {selected_request.get('student_email', '')}")
                        st.markdown(f"**School:** {selected_request.get('student_school', '')}")
                        st.markdown(f"**Major:** {selected_request.get('student_major', '')}")
                        st.markdown(f"**Notes:** {selected_request.get('notes', '')}")

                        if selected_request.get("status", "").strip().lower() == "pending":
                            st.divider()
                            decision = st.radio(
                                "Decision",
                                ["Approved", "Rejected"],
                                key=f"decision_{selected_request['student_email']}",
                            )

                            if st.button(
                                "Record Decision",
                                key=f"record_decision_{selected_request['student_email']}",
                                type="primary",
                                use_container_width=True,
                            ):
                                for request in connection_requests:
                                    if request.get("request_id") == selected_request.get("request_id"):
                                        request["status"] = decision
                                        break
                                save_data(connection_requests, json_connections)
                                st.success("Decision recorded.")
                                st.rerun()
                    else:
                        st.info("Select a request to view details.")

    with tab2:
        left_spacer, center_column, right_spacer = st.columns([1, 4, 1])
        with center_column:
            st.subheader("Manage Connections")
            student_tochange = None
            selected_index_student = None

            user_email = st.session_state["user"]["email"].strip().lower()
            filtered_students = [
                request
                for request in connection_requests
                if request.get("advisor_email", "").strip().lower() == user_email
                and request.get("status", "").strip().lower() == "approved"
            ]

            display_students = [
                {
                    "Student Name": student.get("student_name", ""),
                    "Student Email": student.get("student_email", ""),
                    "School": student.get("student_school", ""),
                    "Major": student.get("student_major", ""),
                }
                for student in filtered_students
            ]

            event = st.dataframe(
                display_students,
                on_select="rerun",
                selection_mode="single-row",
                use_container_width=True,
                key="manage_connections_table_student",
            )

            if event.selection.rows:
                selected_index_student = event.selection.rows[0]
                student_tochange = filtered_students[selected_index_student]

            if student_tochange is not None:
                edit_name_student = st.text_input(
                    "Full Name",
                    value=student_tochange.get("student_name", ""),
                    key="edit_name_student",
                )
                edit_email_student = st.text_input(
                    "Email",
                    value=student_tochange.get("student_email", ""),
                    key="edit_email_student",
                )
                edit_school_student = st.text_input(
                    "School",
                    value=student_tochange.get("student_school", ""),
                    key="edit_school_student",
                )
                edit_major_student = st.text_input(
                    "Major",
                    value=student_tochange.get("student_major", ""),
                    key="edit_major_student",
                )

                col1, col2 = st.columns(2)
                with col1:
                    update_btn = st.button(
                        "Update Connection",
                        key=f"btn_update_student_{selected_index_student}",
                        use_container_width=True,
                        type="primary",
                    )
                with col2:
                    delete_btn = st.button(
                        "Delete Connection",
                        key=f"btn_delete_student_{selected_index_student}",
                        use_container_width=True,
                    )

                if update_btn:
                    student_tochange["student_name"] = edit_name_student
                    student_tochange["student_email"] = edit_email_student
                    student_tochange["student_school"] = edit_school_student
                    student_tochange["student_major"] = edit_major_student
                    save_data(connection_requests, json_connections)
                    st.success("Connection is updated!")
                    st.rerun()

                if delete_btn:
                    for request in connection_requests:
                        if request.get("request_id") == student_tochange.get("request_id"):
                            connection_requests.remove(request)
                            break
                    save_data(connection_requests, json_connections)
                    st.success("Connection deleted!")
                    st.rerun()
            else:
                if not filtered_students:
                    st.info("No approved connections yet.")
                else:
                    st.info("Select a connection to edit.")


def render_student_home(users: list, connection_requests: list) -> None:
    st.header(f"Welcome, {st.session_state['user']['full_name']}!")
    st.subheader("Your Network")

    user_email = st.session_state["user"]["email"].strip().lower()

    user_connections = [
    req for req in connection_requests
    if req.get("student_email","").strip().lower() == user_email]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.metric("Total Connections", len(user_connections))

    with col2:
        with st.container(border=True):
            st.metric(
                "Approved Requests",
                len([req for req in user_connections if req.get("status","").lower() == "approved"])
            )

    with col3:
        with st.container(border=True):
            st.metric(
                "Pending Requests",
                len([req for req in user_connections if req.get("status","").lower() == "pending"])
            )

    with col4:
        with st.container(border=True):
            st.metric("Emails Sent", len(logs))


    left, right = st.columns([2, 1])
    with left:
        with st.container(border=True):
            user_email = st.session_state["user"]["email"].strip().lower()

            user_connections = [
                conn for conn in connection_requests
                if conn.get("student_email", "").strip().lower() == user_email
            ]

            if user_connections:
                st.subheader("Recent Connections")

                recent_connections = user_connections[-7:]

                for conn in recent_connections:
                    with st.container(border=True):
                        col1, col2 = st.columns([3,1])

                        with col1:
                            st.markdown(
                                f"**{conn.get('advisor_name', '')}**  \n"
                                f"{conn.get('advisor_company', '')}"
                            )

                        with col2:
                            status = conn.get('status', '')

                            if status == "Approved":
                                st.success(status)
                            elif status == "Pending":
                                st.warning(status)
                            elif status == "Rejected":
                                st.error(status)
                            else:
                                st.info(status)
            else:
                st.info("No connections yet. Start by sending a connection request!")

    with right:
        with st.container(border=True):
            st.subheader("Your Details")
            st.write(f"**Name:** {st.session_state['user']['full_name']}")
            st.write(f"**Email:** {st.session_state['user']['email']}")
            st.write(f"**Major:** {st.session_state['user'].get('major', 'Not Provided')}")
            st.write(f"**School:** {st.session_state['user'].get('school', 'Not Provided')}")
            st.write(f"**Grad Year:** {st.session_state['user'].get('grad_year', 'Not Provided')}")

        with st.container(border=True):
            resume_path = f"resumes/{st.session_state['user']['email']}.pdf"

            if os.path.exists(resume_path):
                st.session_state["resume_uploaded"] = True
            else:
                st.session_state["resume_uploaded"] = False


            if "resume_uploaded" not in st.session_state:
                st.session_state["resume_uploaded"] = False

            if "resume_name" not in st.session_state:
                st.session_state["resume_name"] = ""

            if st.session_state["resume_uploaded"] == False:
                uploaded_resume = st.file_uploader("Upload Your Resume", type=["pdf"])

                if uploaded_resume is not None:
                    save_resume(uploaded_resume, st.session_state["user"]["email"])

                    st.session_state["resume_uploaded"] = True
                    st.session_state["resume_name"] = uploaded_resume.name

                    st.success("Resume uploaded successfully!")
                    st.rerun()

            else:
                st.subheader("Your Resume")
                st.download_button(
                label=st.session_state["resume_name"],
                data=open(f"resumes/{st.session_state['user']['email']}.pdf", "rb"),
                file_name=st.session_state["resume_name"],
                mime="application/pdf",
                use_container_width=True)

                if st.button("**Remove Resume**", type="secondary", use_container_width=True ):
                    st.session_state["resume_uploaded"] = False
                    st.rerun()

        with st.container(border=True):
            st.subheader("Quick Actions")

            if st.button("➕ Add Connection", use_container_width=True):
                st.session_state.page = "student_dashboard"
            if st.button("✉️ Generate Email", use_container_width=True):
                st.session_state.page = "AI_email_helper"
            if st.button("👥 View All Connections", use_container_width=True):
                st.session_state.page = "student_dashboard"


def render_student_dashboard(users: list, connection_requests: list) -> None:
    st.markdown("### Here is your Network!")
    tab1, tab2, tab3 = st.tabs(["Add Connections", "Manage Connections", "Pending Requests"])

    with tab1:
        left_spacer, center_column, right_spacer = st.columns([1, 4, 1])
        with center_column:
            st.subheader("Request a Connection")
            st.markdown("Send a networking request to an advisor.")

            advisor_options = get_advisor_options(users)
            selected_advisor = st.selectbox("Choose an Advisor", advisor_options, placeholder="--Select an Advisor--")

            student_name = st.text_input(
                "Your Name",
                value=st.session_state["user"].get("full_name", ""),
                placeholder="John Doe",
                key="student_name_input",
            )
            student_email = st.text_input(
                "Your Email",
                value=st.session_state["user"].get("email", ""),
                placeholder="john.doe@udel.edu",
                key="student_email_input",
            )
            student_school = st.text_input(
                "School",
                value=st.session_state["user"].get("school", ""),
                placeholder="University of Delaware",
                key="student_school_input",
            )
            student_major = st.text_input(
                "Major",
                value=st.session_state["user"].get("major", ""),
                placeholder="Computer Science",
                key="student_major_input",
            )
            notes = st.text_area("Message to Advisor",
                height=100, key="notes_input", 
                placeholder="Write a brief message to the advisor explaining why you'd like to connect and what you're hoping to learn from them.")

            if st.button("Submit Request", type="primary", use_container_width=True):
                if not student_name or not student_email or not notes:
                    st.warning("Please fill out all required fields.")
                else:
                    advisor = find_advisor_by_label(users, selected_advisor)
                    if advisor is not None:
                        add_connection_request(
                            connection_requests,
                            student_name,
                            student_email,
                            student_school,
                            student_major,
                            advisor.get("full_name", ""),
                            advisor.get("email", ""),
                            advisor.get("company", ""),
                            notes,
                        )
                        save_data(connection_requests, json_connections)
                        st.success("Request sent!")
                        time.sleep(1)
                        st.rerun()

    with tab2:
        left_spacer, center_column, right_spacer = st.columns([1, 4, 1])
        with center_column:
            st.subheader("Manage Connections")
            advisor_tochange = None
            selected_index = None

            user_email = st.session_state["user"]["email"].strip().lower()
            connected_advisor_emails = [
                request.get("advisor_email", "").strip().lower()
                for request in connection_requests
                if request.get("student_email", "").strip().lower() == user_email
                and request.get("status", "").strip().lower() == "approved"
                and request.get("advisor_email", "").strip() != ""
            ]

            filtered_advisors = [
                advisor
                for advisor in users
                if advisor.get("role", "").strip().lower() == "advisor"
                and advisor.get("email", "").strip().lower() in connected_advisor_emails
            ]

            display_advisors = [
                {
                    "Name": advisor.get("full_name", ""),
                    "Email": advisor.get("email", ""),
                    "Company": advisor.get("company", ""),
                    "Position": advisor.get("position", ""),
                }
                for advisor in filtered_advisors
            ]

            event = st.dataframe(
                display_advisors,
                on_select="rerun",
                selection_mode="single-row",
                use_container_width=True,
                key="manage_connections_table",
            )

            if event.selection.rows:
                selected_index = event.selection.rows[0]
                advisor_tochange = filtered_advisors[selected_index]

            if advisor_tochange is not None:
                edit_name = st.text_input(
                    "Full Name",
                    value=advisor_tochange.get("full_name", ""),
                    key="edit_full_name",
                    placeholder="John Doe",
                )
                edit_email = st.text_input(
                    "Email",
                    value=advisor_tochange.get("email", ""),
                    key="edit_email",
                    placeholder="john.doe@company.com",
                )
                edit_company = st.text_input(
                    "Company",
                    value=advisor_tochange.get("company", ""),
                    key="edit_company",
                    placeholder="Company Name",
                )
                edit_position = st.text_input(
                    "Position",
                    value=advisor_tochange.get("position", ""),
                    key="edit_position",
                    placeholder="Position Title",
                )

                col1, col2 = st.columns(2)
                with col1:
                    update_btn = st.button(
                        "Update Connection",
                        key=f"btn_update_{selected_index}",
                        use_container_width=True,
                        type="primary",
                    )
                with col2:
                    delete_btn = st.button(
                        "Delete Connection",
                        key=f"btn_delete_{selected_index}",
                        use_container_width=True,
                    )

                if update_btn:
                    advisor_tochange["full_name"] = edit_name
                    advisor_tochange["email"] = edit_email
                    advisor_tochange["company"] = edit_company
                    advisor_tochange["position"] = edit_position
                    save_data(users, json_users)
                    st.success("Connection is updated!")
                    st.rerun()

                if delete_btn:
                    for request in connection_requests:
                        if (
                            request.get("student_email", "").strip().lower() == user_email
                            and request.get("advisor_email", "").strip().lower()
                            == advisor_tochange.get("email", "").strip().lower()
                            and request.get("status", "").strip().lower() == "approved"
                        ):
                            connection_requests.remove(request)
                            break
                    save_data(connection_requests, json_connections)
                    st.success("Connection deleted!")
                    st.rerun()
            else:
                if not filtered_advisors:
                    st.info("No approved connections yet.")
                else:
                    st.info("Select a connection to edit.")

    with tab3:
        left_spacer, center_column, right_spacer = st.columns([1, 4, 1])
        with center_column:
            st.markdown("### Pending Requests")
            st.markdown("This is where students can view pending connection requests.")
            pending = []

            for request in connection_requests:
                if (
                    request.get("status", "").strip().lower() == "pending"
                    and request.get("student_email", "").strip().lower()
                    == st.session_state["user"]["email"].strip().lower()
                ):
                    pending.append(
                        {
                            "Status": request.get("status", ""),
                            "Advisor": request.get("advisor_name", ""),
                            "Company": request.get("advisor_company", ""),
                        }
                    )

            st.dataframe(pending if pending else [], use_container_width=True)
