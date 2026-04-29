import streamlit as st
import json
from pathlib import Path
import uuid
import time
import os
from dotenv import load_dotenv
from openai import OpenAI


json_users = Path("users.json")
json_connections = Path("connections.json")
json_AI_EMAIL = Path('email_context.json')
json_logs = Path('logs.json')

users = [
    {
        "id": "1",
        "email": "emdesmo@udel.edu",
        "full_name": "Emily Desmond",
        "password": "testing123",
        "role": "Student",
        "school": "University of Delaware",
        "major": "Management Information Systems",
        "grad_year": 2026
    },
    {
        "id": "2",
        "email": "joedoe@udel.edu",
        "full_name": "Joe Doe",
        "password": "testing123",
        "role": "Advisor",
        "company": "Tech Solutions",
        "position": "Senior Software Engineer"
    }
]

connections = [
    {
        "request_id": "011101",
        "status": "Pending",
        "advisor_email": "joedoe@udel.edu",
        "advisor_name": "Joe Doe",
        "advisor_company": "Tech Solutions",
        "student_email": "emdesmo@udel.edu",
        "student_name": "Emily Desmond",
        "student_school": "University of Delaware",
        "student_major": "Management Information Systems",
        "notes": "I would love to hear about your experience in the tech industry and any advice you have for someone starting out.",
        "advisor_note": ""
    }
]

ai_email_context = []

logs = []


# ================= Data Layer =================
def load_data(json_path: Path, default_data: list) -> list:
    import json 

    if json_path.exists() and json_path.stat().st_size > 0:

        with open(json_path, "r", encoding="utf-8") as f:

            return json.load(f)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(default_data, f, indent=4)

    return default_data.copy()



def save_data(data: list, json_path: Path) -> None:
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ================= Service Layer =================
def create_account(users: list, full_name: str, email: str, password: str, role: str):
    existing_emails = [user.get("email", "").strip().lower() for user in users]

    if email.strip().lower() in existing_emails:
        return None

    new_user = {
        "id": str(uuid.uuid4()),
        "email": email.strip(),
        "full_name": full_name.strip(),
        "password": password,
        "role": role,
    }
    users.append(new_user)
    return new_user



def authenticate_user(users: list, email: str, password: str):
    return next(
        (
            user
            for user in users
            if user.get("email", "").strip().lower() == email.strip().lower()
            and user.get("password") == password
        ),
        None,
    )



def update_profile(users: list, current_email: str, full_name: str, email: str, school: str, major: str):
    for user in users:
        if user.get("email", "").strip().lower() == current_email.strip().lower():
            user["full_name"] = full_name.strip()
            user["email"] = email.strip()
            user["school"] = school.strip()
            user["major"] = major.strip()
            return user
    return None



def add_connection_request(
    connection_requests: list,
    student_name: str,
    student_email: str,
    student_school: str,
    student_major: str,
    advisor_name: str,
    advisor_email: str,
    advisor_company: str,
    notes: str,
) -> None:
    connection_requests.append(
        {
            "request_id": str(uuid.uuid4()),
            "student_email": student_email.strip(),
            "student_name": student_name.strip(),
            "student_school": student_school.strip(),
            "student_major": student_major.strip(),
            "advisor_email": advisor_email.strip(),
            "advisor_name": advisor_name.strip(),
            "advisor_company": advisor_company.strip(),
            "status": "Pending",
            "notes": notes.strip(),
            "advisor_note": "",
        }
    )



def get_advisor_options(users: list) -> list:
    return [
        f"{advisor['full_name']} - {advisor.get('company', '')}"
        for advisor in users
        if advisor.get("role", "").strip().lower() == "advisor"
    ]



def find_advisor_by_label(users: list, selected_advisor: str) -> dict:
    advisor_name, advisor_company = selected_advisor.split(" - ", 1)
    return next(
        (
            advisor
            for advisor in users
            if advisor.get("full_name") == advisor_name
            and advisor.get("company", "") == advisor_company
        ),
        None,
    )


# ================= UI Layer =================
def render_signup(users: list) -> None:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.header("Network Manager :globe_with_meridians:")

    st.divider()
    st.subheader("Create an Account")

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
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = new_user
                    st.session_state["role"] = role_signup

                    with st.spinner("Creating account..."):
                        time.sleep(2)

                    st.success(f"Account created! Welcome, {full_name_signup}!")
                    st.session_state["page"] = "profile_setup"
                    st.rerun()

        if st.button("Have an Account? Log In", type="secondary", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()



def render_profile_setup(users: list) -> None:
    if st.session_state["user"] is None:
        st.warning("Please log in first.")
        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("### Profile Setup")

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

    if st.button("Complete Profile", type="primary", use_container_width=True):
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

        st.success("Profile setup complete!")

        if st.session_state["role"] == "Student":
            st.session_state["page"] = "student_home_page"
        else:
            st.session_state["page"] = "advisor_home_page"

        st.rerun()



def render_login(users: list) -> None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.header("Network Manager :globe_with_meridians:")

    st.divider()

    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:
        st.subheader("Log In")

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
    st.markdown("This is the Advisor Home Page")
    st.markdown(f"### Welcome, {st.session_state['user']['full_name']}!")
    st.subheader("Your Network")
    st.divider()

    pending_students = []
    for request in connection_requests:
        if (
            request.get("status", "").strip().lower() == "pending"
            and request.get("advisor_email", "").strip().lower()
            == st.session_state["user"]["email"].strip().lower()
        ):
            pending_students.append(
                {
                    "Status": request.get("status", ""),
                    "Student": request.get("student_name", ""),
                    "School": request.get("student_school", ""),
                }
            )

    col1, col2, col3 = st.columns([4, 3, 3])

    with col1:
        st.markdown("## Pending Requests")
        st.dataframe(pending_students if pending_students else [], use_container_width=True)

    with col2:
        st.markdown("### UNDER CONSTRUCTION")
        with st.container(border=True):
            st.markdown("### Upcoming Events")
            st.markdown("Under Construction")

    with col3:
        with st.container(border=True):
            st.button("Click me for a surprise!", use_container_width=True, on_click=lambda: st.balloons())



def render_advisor_dashboard(users: list, connection_requests: list) -> None:
    st.markdown("### Network!")
    tab1, tab2 = st.tabs(["Students", "Manage Connections"])

    with tab1:
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



def render_student_home(users: list) -> None:
    st.header(f"Welcome, {st.session_state['user']['full_name']}!")
    st.subheader("Your Network")
    st.divider()

    profile_found = False
    col1, col2, col3 = st.columns([3, 3, 3])

    with col1:
        with st.container(border=True):
            st.markdown("### Bubble")

    with col2:
        with st.container(border=True):
            st.markdown("### Resume")
            with st.expander("Upload Your Resume"):
                st.file_uploader("Choose a file", type=["pdf", "docx"], key="resume_uploader")

        with st.container(border=True):
            st.markdown("### Bubble")

    with col3:
        with st.container(border=True):
            st.markdown("### Your Details")
            for prof in users:
                if prof.get("email", "").strip().lower() == st.session_state["user"]["email"].strip().lower():
                    profile_found = True
                    st.markdown(f"**Name:** {prof.get('full_name', '')}")
                    st.markdown(f"**Email:** {prof.get('email', '')}")
                    st.markdown(f"**Major:** {prof.get('major', '')}")
                    st.markdown(f"**School:** {prof.get('school', '')}")
                    st.markdown(f"**Grad Year:** {prof.get('grad_year', '')}")

            if not profile_found:
                st.info("Complete your profile to see your details here.")



def render_student_dashboard(users: list, connection_requests: list) -> None:
    st.markdown("### Here is your Network!")
    tab1, tab2, tab3 = st.tabs(["Add Connections", "Manage Connections", "Pending Requests"])

    with tab1:
        st.subheader("Request a Connection")
        st.markdown("Send a networking request to an advisor.")

        advisor_options = get_advisor_options(users)
        selected_advisor = st.selectbox("Choose an Advisor", advisor_options)

        student_name = st.text_input(
            "Your Name",
            value=st.session_state["user"].get("full_name", ""),
            placeholder="John Doe",
        )
        student_email = st.text_input(
            "Your Email",
            value=st.session_state["user"].get("email", ""),
            placeholder="john.doe@udel.edu",
        )
        student_school = st.text_input(
            "School",
            value=st.session_state["user"].get("school", ""),
            placeholder="University of Delaware",
        )
        student_major = st.text_input(
            "Major",
            value=st.session_state["user"].get("major", ""),
            placeholder="Computer Science",
        )
        notes = st.text_area("Message to Advisor", height=120)

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



def render_ai_email_helper() -> None:
    st.markdown("### AI Email Helper")

    def get_data(json_AI_EMAIL):
        if not json_AI_EMAIL.exists():
            return "[]"
        with open(json_AI_EMAIL, "r") as f:
            data = json.load(f)
            return json.dumps(data, indent=2)

    def load_logs(json_logs):
        if json_logs.exists():
            with open(json_logs, "r") as f:
                return json.load(f)
        else:
            return []

    def save_logs(json_logs, logs):
        with open(json_logs, "w") as f:
            json.dump(logs, f, indent=2)

    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY was not found. Check your .env file.")
        st.stop()
    client = OpenAI(api_key=api_key)

    email_context = get_data(json_AI_EMAIL)

    if "messages" not in st.session_state:
        st.session_state.messages = []
        logs = load_logs(json_logs)
        for log in logs:
            st.session_state.messages.append({"role": "user", "content":
            log["user_message"]})
            st.session_state.messages.append({"role": "assistant", "content":
            log["assistant_message"]})
    # If there is no saved history, show a starter assistant bubble
        if len(st.session_state.messages) == 0:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Hi! Ask me a question about writing the perfect email."
    })

    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_input = st.chat_input("Type your question...")
    if user_input:
    # Update state and UI with user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container.chat_message("user"):
            st.markdown(user_input)

    # --- Service Layer ---
    def build_ai_prompt(email_context):
        "Builds the hidden instructions and business context for the AI."""
        return (
        "You are a helpful company assistant.\n"
        "Answer user questions based ONLY on the email data provided below.\n"
        "If the answer is not in the email data, say you do not have enough information.\n\n"
        f"ORDER DATA:\n{email_context}"
    )

    def get_ai_response(client: OpenAI, email_context: str, chat_history: list):
            "Combines hidden instructions with visible chat history, then calls the AI."
            ai_prompt = build_ai_prompt(email_context)
            ai_prompt_message = [{"role": "system", "content": ai_prompt}]
            messages = ai_prompt_message + chat_history
            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2
    )
            return response.choices[0].message.content

    # Get AI response and update UI
    with chat_container.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_text = get_ai_response(client, email_context,
            st.session_state.messages)
            st.markdown(response_text)

    # Update state with AI response
    st.session_state.messages.append({"role": "assistant", "content":
    response_text})
    # Log the interaction. In a real app we'd maintain the array in session state,
    # but here we load, append, and save directly to the file to keep state simple.
    logs = load_logs(json_logs)
    logs.append({"user_message": user_input, "assistant_message": response_text})
    save_logs(json_logs, logs)
    # Do we need st.rerun() here?
    # NO! Because we manually drew the new messages into the `chat_container` using
    # `with chat_container.chat_message(...)`, the UI is already visually up to date.
    # Streamlit will automatically persist them from session state on the next natural run.


def render_sidebar() -> None:
    if not st.session_state["logged_in"]:
        return

    with st.sidebar:
        st.markdown("### Move From Page to Page")

        if st.session_state["role"] == "Student":
            if st.button("Home", key="home_btn"):
                st.session_state["page"] = "student_home_page"
                st.rerun()
            if st.button("Dashboard", key="dash_btn"):
                st.session_state["page"] = "student_dashboard"
                st.rerun()
            if st.button("AI Email Helper", key="ai_btn"):
                st.session_state["page"] = "AI_email_helper"
                st.rerun()
            if st.button("Profile", key="profile_btn"):
                st.session_state["page"] = "profile_setup"
                st.rerun()
            if st.button("Log Out", key="logout_btn"):
                with st.spinner("logging out..."):
                    time.sleep(2)
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["page"] = "login"
                st.rerun()

        if st.session_state["role"] == "Advisor":
            if st.button("Home", key="home_btn_2"):
                st.session_state["page"] = "advisor_home_page"
                st.rerun()
            if st.button("Dashboard", key="dash_btn_2"):
                st.session_state["page"] = "advisor_dashboard"
                st.rerun()
            if st.button("Log Out", key="logout_btn_2"):
                with st.spinner("logging out..."):
                    time.sleep(2)
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["page"] = "login"
                st.rerun()


# ================= Main App =================
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
        layout="centered",
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
        render_login(users)
    elif current_role == "Advisor":
        if current_page == "advisor_home_page":
            render_advisor_home(loaded_connection_requests)
        elif current_page == "advisor_dashboard":
            render_advisor_dashboard(loaded_users, loaded_connection_requests)
    elif current_role == "Student":
        if current_page == "student_home_page":
            render_student_home(loaded_users)
        elif current_page == "student_dashboard":
            render_student_dashboard(loaded_users, loaded_connection_requests)
        elif current_page == "AI_email_helper":
            render_ai_email_helper()

    render_sidebar()


if __name__ == "__main__":
    main()
