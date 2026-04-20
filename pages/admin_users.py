import streamlit as st

PAGE_NAME = "Users"
SECTION_NAME = "Admin"
URL_PATH = "admin-users"
PRIORITY = 100
REQUIRED_ROLES = {"admin"}

_ALL_ROLES = ["user", "business_admin", "admin"]


def build_page():
    st.title("User Management")

    auth = st.session_state["auth_controller"]

    with st.expander("Create new user", expanded=False):
        with st.form("create_user_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input(
                "Password", type="password"
            )
            roles = st.multiselect(
                "Roles", _ALL_ROLES, default=["user"]
            )
            if st.form_submit_button("Create user"):
                if not username.strip() or not email.strip() or not password:
                    st.error("All fields are required.")
                else:
                    try:
                        auth.create_user(
                            username=username.strip(),
                            email=email.strip(),
                            password=password,
                            roles=roles,
                        )
                        st.success(
                            f"User '{username}' created."
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    st.subheader("Existing users")
    users = auth.list_users()
    if not users:
        st.info("No users yet.")
        return

    for user in users:
        with st.container(border=True):
            col_info, col_roles, col_active = (
                st.columns([2, 3, 1])
            )
            with col_info:
                st.markdown(f"**{user.username}**")
                st.caption(user.email)

            with col_roles:
                current_roles = [
                    r.name for r in user.roles
                ]
                new_roles = st.multiselect(
                    "Roles",
                    _ALL_ROLES,
                    default=current_roles,
                    key=f"roles_{user.user_id}",
                    label_visibility="collapsed",
                )
                if new_roles != current_roles:
                    if st.button(
                        "Save roles",
                        key=f"save_{user.user_id}",
                    ):
                        auth.set_user_roles(
                            user.user_id, new_roles
                        )
                        st.rerun()

            with col_active:
                active = st.toggle(
                    "Active",
                    value=user.is_active,
                    key=f"active_{user.user_id}",
                )
                if active != user.is_active:
                    auth.set_user_active(
                        user.user_id, active
                    )
                    st.rerun()
