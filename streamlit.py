import streamlit as st

from pages import load_page_sections


def _build_controller():
    from services import get_llm_service
    from services.system_prompt import get_system_prompt_maker
    from controllers.chat_controller import ChatController

    return ChatController(
        chat_service=get_llm_service(
            system_prompt_maker=get_system_prompt_maker()
        )
    )


st.set_page_config(layout="wide")

if "controller" not in st.session_state:
    st.session_state["controller"] = _build_controller()

nav = st.navigation(load_page_sections())
nav.run()
