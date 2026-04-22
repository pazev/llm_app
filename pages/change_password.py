import streamlit as st

PAGE_NAME = "Change Password"
SECTION_NAME = "Account"
URL_PATH = "change-password"
PRIORITY = 90
REQUIRED_ROLES: set = set()  # any logged-in user
HIDE_IF_LOGGED_IN = False


def build_page():
    st.title("Change Password")

    user = st.session_state.get("user")
    auth = st.session_state["auth_controller"]

    with st.form("change_password_form"):
        current = st.text_input(
            "Current password", type="password"
        )
        new = st.text_input(
            "New password", type="password"
        )
        confirm = st.text_input(
            "Confirm new password", type="password"
        )
        submitted = st.form_submit_button(
            "Change password"
        )

    if submitted:
        ok, msg = auth.change_password(
            user_id=user.user_id,
            current_password=current,
            new_password=new,
            confirm_password=confirm,
        )
        if ok:
            st.success(msg)
        else:
            st.error(msg)
