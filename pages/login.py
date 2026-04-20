import streamlit as st

PAGE_NAME = "Login"
SECTION_NAME = "Auth"
URL_PATH = "login"
PRIORITY = 0
REQUIRED_ROLES: set = set()  # public


def build_page():
    st.title("Sign In")

    auth = st.session_state["auth_controller"]

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input(
            "Password", type="password"
        )
        submitted = st.form_submit_button("Sign in")

    if submitted:
        if not username.strip() or not password:
            st.error("Enter username and password.")
        else:
            user = auth.login(username.strip(), password)
            if user is None:
                st.error(
                    "Invalid credentials or inactive"
                    " account."
                )
            else:
                st.session_state["user"] = user
                st.rerun()
