import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time
import re

st.set_page_config(page_title='Network Manager', page_icon=':globe_with_meridians:', layout='centered')

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    
if 'user' not in st.session_state:
    st.session_state['user'] = None

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

if 'role' not in st.session_state:
    st.session_state['role'] = None

users = [
{
"users": [
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
],
"requests": []
}
]

connection_requests = [
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

json_connections = Path("connection_request.json")

if json_connections.exists() and json_connections.stat().st_size > 0:
    with json_connections.open("r", encoding="utf-8") as f:
        connection_requests = json.load(f)

json_users = Path("users.json")

default_data = {"users": [], "requests": []}

if json_users.exists() and json_users.stat().st_size > 0:
    with open(json_users, "r") as f:
        data = json.load(f)

    if isinstance(data, list):
        users = data
        connection_requests = []
    else:
        users = data.get("users", [])
        connection_requests = data.get("requests", [])
else:
    users = []
    connection_requests = []

def save_data():
    with open(json_users, "w") as f:
        json.dump({
            "users": users,
            "requests": connection_requests
        }, f, indent=4)

# ================= Sign Up Screen =================
if st.session_state["page"] == "signup":

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.header("Network Manager :globe_with_meridians:")

    st.divider()

    st.subheader("Create an Account")

    with st.container(border=True): 
        full_name_signup = st.text_input("Full Name", 
            key="full_name_signup", 
            placeholder="John Doe")

        email_signup = st.text_input("Email Address", 
            key="email_signup", 
            placeholder="john.doe@udel.edu")

        password_signup = st.text_input("Password", 
            type="password", 
            key="password_signup", 
            placeholder="Create a strong password")

        role_signup = st.selectbox("Role", ["Student", "Advisor"], key="role_signup")

        if st.button("Create Account", type="primary", use_container_width=True):

            if not full_name_signup or not email_signup or not password_signup:

                st.warning("Please fill out all fields.") 

            else:
                user = next((user for user in users if "email" in user and user["email"].strip().lower() == email_signup.strip().lower()), None)
                existing_emails = [user["email"].strip().lower() for user in users]

                if email_signup.strip().lower() in existing_emails:
                    st.error("An account with this email already exists.") 

                else:
                    st.session_state["logged_in"] = True 
                    st.session_state["user"] = {    
                    "id": str(uuid.uuid4()),
                    "email": email_signup,
                    "full_name": full_name_signup,
                    "password": password_signup,
                    "role": role_signup}

                    st.session_state["role"] = role_signup 
                    users.append(st.session_state["user"]) 

                    with open(json_users, "w") as f:
                        json.dump(users, f, indent=4)

                    with st.spinner("Creating account..."):
                        time.sleep(2)

                    st.success(f"Account created! Welcome, {full_name_signup}!")
                    st.session_state["page"] = "profile_setup"
                    st.rerun()

        if st.button("Have an Account? Log In", type="secondary", use_container_width=True): 
            st.session_state["page"] = "login"
            st.rerun()


# ================= Profile Setup =================
elif st.session_state["page"] == "profile_setup":
    if st.session_state["user"] is None: 
        st.warning("Please log in first.")
        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("### Profile Setup")


    with st.container(border=True): 
            profile_full_name = st.text_input(
                "Student Name",
                value=st.session_state["user"]["full_name"],
                key="profile_full_name")
            
            profile_email = st.text_input(
                "Student Email",
                value=st.session_state["user"]["email"],
                key="profile_email")
            
            profile_school = st.text_input("School",
                value=st.session_state["user"].get("school", ""), 
                key="profile_school")
            
            profile_major = st.text_input("Major", 
                value=st.session_state["user"].get("major", ""), 
                key="profile_major")

    if st.button("Complete Profile", type="primary", use_container_width=True): 
        new_profile = {
            "profile_full_name": profile_full_name,
            "profile_email": profile_email,
            "profile_school": profile_school,
            "profile_major": profile_major
        }

        st.success("Profile setup complete!")

        if st.session_state["role"] == "Student":
            st.session_state["page"] = "student_home_page"
        else:
            st.session_state["page"] = "advisor_home_page"

        st.rerun()


# ================= Log In Screen =================
elif st.session_state["page"] == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.header("Network Manager :globe_with_meridians:")

    st.divider()

    left_spacer, center_column, right_spacer = st.columns([1, 2, 1])
    with center_column:

        st.subheader("Log In")

        with st.container(border=True, width=600):

            email_input = st.text_input("Email Address", 
                key="email_login", 
                placeholder="Enter your email")
            
            password_input = st.text_input("Password", 
                type="password", key="password", 
                placeholder="Enter your password")

            if st.button("Log In", type="primary", use_container_width=True):
                with st.spinner("Logging in..."):
                    time.sleep(2)

                    found_user = None

                user = next((user for user in users if "email" in user and "password" in user and user["email"].strip().lower() == email_input.strip().lower() and user["password"] == password_input), None)
                if user:
                    found_user = user
                    if found_user and found_user["role"] == "Student":
                        st.success(f"Welcome back, {found_user['email']}!")
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = found_user
                        st.session_state["role"] = found_user["role"]
                        st.session_state["page"] = "student_home_page"
                        time.sleep(2)
                        st.rerun()

                    elif found_user and found_user["role"] == "Advisor":
                        st.success(f"Welcome back, {found_user['email']}!")
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = found_user
                        st.session_state["role"] = found_user["role"]
                        st.session_state["page"] = "advisor_home_page"
                        time.sleep(2)
                        st.rerun()

                else:
                    st.error("Invalid email or password. Please try again.")

            if st.button("Don't have an account? Sign Up", type="secondary", use_container_width=True):
                st.session_state["page"] = "signup"
                st.rerun()


# ================= Advisor =================
elif st.session_state["role"] == "Advisor":

    if st.session_state["page"] == "advisor_home_page":
        st.markdown("This is the Advisor Home Page")
        st.markdown(f'### Welcome, {st.session_state["user"]["full_name"]}!')
        st.subheader("Your Network")
        st.divider()

        profile_found = False
        pending_students = []

        for request in connection_requests:
            if request["status"].strip().lower() == "pending" and request["advisor_email"].strip().lower() == st.session_state["user"]["email"].strip().lower():
                pending_students.append({
                    "Status": request["status"],
                    "Student": request.get("student_name", ""),
                    "School": request.get("student_school", ""),
                })

        col1, col2, col3 = st.columns([4, 3, 3])

        with col1:
            st.markdown("## Pending Requests")
            st.dataframe(pending_students if pending_students else [], use_container_width=True)

        with col2:
            st.markdown("###UNDER CONSTRUCTION")

            with st.container(border=True):
                st.markdown("### Upcoming Events")
                st.markdown("Under Construction")

        with col3:
            with st.container(border=True):
                st.button('Click me for a surprise!', use_container_width=True, on_click=lambda: st.balloons())

    elif st.session_state["page"] == "advisor_dashboard":
        st.markdown('### Network!')

        tab1, tab2 = st.tabs(['Students', 'Manage Connections'])

        with tab1:
            st.header("Student Connection Requests")
            st.markdown("This is where advisors can review student connection requests.")

            view_connections = [
                request for request in users
                if request.get("advisor_email", "").strip().lower() == st.session_state["user"]["email"].strip().lower()]

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
                        1 for request in view_connections
                        if request.get("status", "").strip().lower() == "pending"
                    )
                    st.markdown("Pending")
                    st.markdown(f"### {pending_count}")

            st.divider()

            with st.container(border=True):
                filter_col1, filter_col2 = st.columns([4, 2])

                with filter_col1:
                    search_item = st.text_input(
                        "Search by Student Email",
                        key="search_txt_by_email"
                    )

                with filter_col2:
                    selected_status = st.selectbox(
                        "Status",
                        ["All", "Pending", "Approved", "Rejected"],
                        key="selected_status_filter"
                    )

            filtered_requests = users.copy()

            if search_item:
                filtered_requests = [
                    request for request in filtered_requests
                    if search_item.lower() in request.get("connection_email", "").lower()
                ]

            if selected_status != "All":
                filtered_requests = [
                    request for request in filtered_requests
                    if request.get("connection_status", "").strip().lower() == selected_status.lower()
                ]

            display_requests = [
                {
                    "Status": request.get("status", ""),
                    "Student Name": request.get("student_name", ""),
                    "Student Email": request.get("student_email", ""),
                    "School": request.get("student_school", ""),
                    "Major": request.get("student_major", "")
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
                    key="advisor_requests_table"
                )

                if event.selection.rows:
                    selected_index = event.selection.rows[0]
                    selected_request = filtered_requests[selected_index]

            with details_col:
                with st.container(border=True):
                    st.markdown("### Request Details")

                    if selected_request is not None:
                        st.markdown(f"**Status:** {selected_request.get('Status', '')}")
                        st.markdown(f"**Student Name:** {selected_request.get('Student Name', '')}")
                        st.markdown(f"**Student Email:** {selected_request.get('Student Email', '')}")
                        st.markdown(f"**School:** {selected_request.get('School', '')}")
                        st.markdown(f"**Major:** {selected_request.get('Major', '')}")
                        st.markdown(f"**Notes:** {selected_request.get('notes', '')}")

                        if selected_request.get("Status", "").strip().lower() == "pending":
                            st.divider()

                            decision = st.radio(
                                "Decision",
                                ["Approved", "Rejected"],
                                key=f"decision_{selected_request['Student Email']}"
                            )

                            if st.button(
                                "Record Decision",
                                key=f"record_decision_{selected_request['Student Email']}",
                                type="primary",
                                use_container_width=True
                            ):
                                for request in users:
                                    if request["request_id"] == selected_request["request_id"]:
                                        request["status"] = decision
                                        break

                                with open(json_users, "w", encoding="utf-8") as f:
                                    json.dump(users, f, indent=4)

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
            request for request in connection_requests
            if request.get("advisor_email", "").strip().lower() == user_email
            and request.get("status", "").strip().lower() == "approved"]

            display_students = [ {
            "Student Name": student.get("student_name", ""),
            "Student Email": student.get("student_email", ""),
            "School": student.get("student_school", ""),
            "Major": student.get("student_major", "") }
            for student in filtered_students]

            event = st.dataframe(
            display_students,
            on_select="rerun",
            selection_mode="single-row",
            use_container_width=True,
            key="manage_connections_table_student")

            if event.selection.rows:
                selected_index_student = event.selection.rows[0]
                student_tochange = filtered_students[selected_index_student]

            if student_tochange is not None:
                edit_name_student = st.text_input(
                "Full Name",
                value=student_tochange.get("student_name", ""),
                key="edit_name_student")

                edit_email_student = st.text_input(
                "Email",
                value=student_tochange.get("student_email", ""),
                key="edit_email_student")

                edit_school_student = st.text_input(
                "School",
                value=student_tochange.get("student_school", ""),
                key="edit_school_student")

                edit_major_student = st.text_input(
                "Major",
                value=student_tochange.get("student_major", ""),
                key="edit_major_student" )

                col1, col2 = st.columns(2)

                with col1:
                    update_btn = st.button(
                    "Update Connection",
                    key=f"btn_update_{selected_index_student}",
                    use_container_width=True,
                    type="primary")

                with col2:
                    delete_btn = st.button(
                    "Delete Connection",
                    key=f"btn_delete_{selected_index_student}",
                    use_container_width=True)

                if update_btn:
                    student_tochange["student_name"] = edit_name_student
                    student_tochange["student_email"] = edit_email_student
                    student_tochange["student_school"] = edit_school_student
                    student_tochange["student_major"] = edit_major_student
                    with json_connections.open("w", encoding="utf-8") as f:
                        json.dump(connection_requests, f, indent=4)

                st.success("Connection is updated!")
                st.rerun()

                if delete_btn:
                    for request in connection_requests:
                        if request["request_id"] == student_tochange["request_id"]:
                            connection_requests.remove(request)
                            break

                    with json_connections.open("w", encoding="utf-8") as f:
                        json.dump(connection_requests, f, indent=4)

                    st.success("Connection deleted!")
                    st.rerun()
            else:
                if not filtered_students:
                    st.info("No approved connections yet.")
                else:
                    st.info("Select a connection to edit.")


# ================= Student =================
elif st.session_state["role"] == "Student":

    if st.session_state["page"] == "student_home_page":
        st.header(f'Welcome, {st.session_state["user"]["full_name"]}!')
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
                    #save resume to user profile in users.json

            with st.container(border=True):
                with st.container(border=True):
                    st.markdown("### Bubble")

        with col3:
            with st.container(border=True):
                st.markdown("### Your Details")

                for prof in users:
                    if prof["email"].strip().lower() == st.session_state["user"]["email"].strip().lower():
                        profile_found = True
                        st.markdown(f"**Name:** {prof.get('full_name','')}")
                        st.markdown(f"**Email:** {prof.get('email','')}")
                        st.markdown(f"**Major:** {prof.get('major','')}")
                        st.markdown(f"**School:** {prof.get('school','')}")
                        st.markdown(f"**Grad Year:** {prof.get('grad_year','')}")

                if not profile_found:
                    st.info("Complete your profile to see your details here.")

    elif st.session_state["page"] == "student_dashboard":
        st.markdown('### Here is your Network!')

        tab1, tab2, tab3 = st.tabs(['Add Connections', 'Manage Connections', 'Pending Requests'])

        with tab1:
            st.subheader("Request a Connection")
            st.markdown("Send a networking request to an advisor.")

            advisor_options = [f"{advisor['full_name']} - {advisor['company']}" for advisor in users if advisor["role"].strip().lower() == "advisor"]
            selected_advisor = st.selectbox("Choose an Advisor", advisor_options)

            student_name = st.text_input("Your Name", placeholder="John Doe")
            student_email = st.text_input("Your Email", placeholder="john.doe@udel.edu")
            student_school = st.text_input("School", placeholder="University of Delaware")
            student_major = st.text_input("Major", placeholder="Computer Science")
            notes = st.text_area("Message to Advisor", height=120)

            if st.button("Submit Request", type="primary", use_container_width=True):
                if not student_name or not student_email or not notes:
                    st.warning("Please fill out all required fields.")
                else:
                    advisor_name = selected_advisor.split(" - ")[0]
                    advisor_company = selected_advisor.split(" - ")[1]

                    advisor_email = ""
                    for advisor in users:
                        if advisor["full_name"] == advisor_name and advisor["company"] == advisor_company:
                            advisor_email = advisor["email"]
                            break

                    new_request = {
                        "request_id": str(uuid.uuid4()),
                        "student_email": student_email,
                        "student_name": student_name,
                        "student_school": student_school,
                        "student_major": student_major,
                        "advisor_email": advisor_email,
                        "advisor_name": advisor_name,
                        "advisor_company": advisor_company,
                        "Status": "Pending",
                        "notes": notes
                    }

                    connection_requests.append(new_request)     
                    with open(json_users, "w") as f:
                        json.dump(users, f, indent=4)

                    st.success("Request sent!")
                    time.sleep(2)
                    st.rerun()

        with tab2:
            st.subheader("Manage Connections")

            advisor_tochange = None
            selected_index = None

            user_email = st.session_state["user"]["email"]

            connected_advisor_emails = [
                request.get("advisor_email", "").strip().lower()
                for request in connection_requests
                if request.get("student_email", "").strip().lower() == user_email.strip().lower()
                and request.get("status", "").strip().lower() == "approved"
                and request.get("advisor_email", "").strip() != ""]

            filtered_advisors = [
            advisor for advisor in users
            if advisor.get("role", "").strip().lower() == "advisor" and 
            advisor.get("email", "").strip().lower() in connected_advisor_emails]

            event = st.dataframe(
                filtered_advisors,
                on_select="rerun",
                selection_mode="single-row",
                use_container_width=True,
                key="manage_connections_table"
            )

            if event.selection.rows:
                selected_index = event.selection.rows[0]
                advisor_tochange = filtered_advisors[selected_index]

            if advisor_tochange is not None:
                edit_name = st.text_input("Full Name", value=advisor_tochange.get("full_name", ""), key="edit_full_name", placeholder="John Doe")
                edit_email = st.text_input("Email", value=advisor_tochange.get("email", ""), key="edit_email", placeholder="john.doe@company.com")
                edit_company = st.text_input("Company", value=advisor_tochange.get("company", ""), key="edit_company", placeholder="Company Name")
                edit_position = st.text_input("Position", value=advisor_tochange.get("position", ""), key="edit_position", placeholder="Position Title")

                col1, col2 = st.columns(2)

                with col1:
                    update_btn = st.button(
                        "Update Connection",
                        key=f"btn_update_{selected_index}",
                        use_container_width=True,
                        type="primary"
                    )

                with col2:
                    delete_btn = st.button(
                        "Delete Connection",
                        key=f"btn_delete_{selected_index}",
                        use_container_width=True
                    )

                if update_btn:
                    advisor_tochange["full_name"] = edit_name
                    advisor_tochange["email"] = edit_email
                    advisor_tochange["company"] = edit_company
                    advisor_tochange["position"] = edit_position

                    with json_connections.open("w", encoding="utf-8") as f:
                        json.dump(connection_requests, f, indent=4)

                    st.success("Connection is updated!")
                    st.rerun()

                if delete_btn:
                    for request in connection_requests:
                        if (
                            request.get("student_email", "").strip().lower() == user_email.strip().lower()
                            and request.get("advisor_email", "").strip().lower() == advisor_tochange.get("email", "").strip().lower()
                            and request.get("status", "").strip().lower() == "approved"
                        ):
                            connection_requests.remove(request)
                            break

                    with json_connections.open("w", encoding="utf-8") as f:
                        json.dump(connection_requests, f, indent=4)

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
                if request["Status"].strip().lower() == "pending" and request["advisor_email"].strip().lower() == st.session_state["user"]["email"].strip().lower():
                        pending.append({
                    "Status": request["Status"],
                    "Advisor": request.get("advisor_name", ""),
                    "Company": request.get("advisor_company", ""),
                })

            st.dataframe(pending if pending else [], use_container_width=True)


    elif st.session_state["page"] == "AI_email_helper":
        st.markdown("### AI Email Helper")
        st.markdown("This is where students can get help drafting emails to advisors.")
        st.markdown("Under Construction")


# ================= Page Navigation in Sidebar =================
if st.session_state["logged_in"]:
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
                    time.sleep(4)
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
                    time.sleep(4)
                    st.session_state["logged_in"] = False
                    st.session_state["user"] = None
                    st.session_state["role"] = None
                    st.session_state["page"] = "login"
                    st.rerun()