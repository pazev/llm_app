import streamlit as st

from pages import load_page_sections, load_page_urls


def _build_controller():
    from controllers.chat_controller import ChatController
    from services_llm import get_llm_service
    from services_llm.system_prompt import (
        get_system_prompt_maker,
    )

    return ChatController(
        chat_service=get_llm_service(
            system_prompt_maker=get_system_prompt_maker()
        )
    )


def _build_auth_controller():
    from controllers.auth_controller import AuthController

    return AuthController()


st.set_page_config(layout="wide")

if "bootstrapped" not in st.session_state:
    from services.bootstrap import bootstrap
    bootstrap()
    st.session_state["bootstrapped"] = True

if "auth_controller" not in st.session_state:
    st.session_state["auth_controller"] = (
        _build_auth_controller()
    )

user = st.session_state.get("user")

if user is None:
    login_page = load_page_urls().get("login")
    nav = st.navigation([login_page])
    nav.run()
    st.stop()

user_roles = {r.name for r in user.roles}

if "controller" not in st.session_state:
    st.session_state["controller"] = _build_controller()

with st.sidebar:
    st.caption(
        f"Signed in as **{user.username}**"
        f" · {', '.join(sorted(user_roles)) or 'no roles'}"
    )
    if st.button("Sign out", use_container_width=True):
        del st.session_state["user"]
        del st.session_state["controller"]
        st.rerun()

nav = st.navigation(
    load_page_sections(user_roles=user_roles, logged_in=True)
)
nav.run()
