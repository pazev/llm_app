import streamlit as st

from services import get_llm_service
from controllers.chat_controller import ChatController
from pages import load_page_sections


def _build_controller() -> ChatController:
    return ChatController(chat_service=get_llm_service())


st.set_page_config(layout="wide")

if "controller" not in st.session_state:
    st.session_state["controller"] = _build_controller()

nav = st.navigation(load_page_sections())
nav.run()
