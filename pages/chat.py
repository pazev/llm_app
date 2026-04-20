import streamlit as st

from pages.utils.message import render_message

PAGE_NAME = "Chat"
SECTION_NAME = "Main"
URL_PATH = "chat"
PRIORITY = 1


def _get_controller():
    return st.session_state["controller"]


def _render_sidebar():
    controller = _get_controller()
    with st.sidebar:
        st.subheader("Model")
        models = controller.list_available_models()
        current = st.session_state.get(
            "selected_model", models[0]
        )
        selected = st.selectbox(
            "Model",
            models,
            index=models.index(current),
            label_visibility="collapsed",
        )
        if selected != current:
            st.session_state["selected_model"] = (
                selected
            )
            controller.set_model(selected)


def build_page():
    _render_sidebar()
    st.title("Business Chat Assistant")

    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = None
        st.session_state["messages"] = []

    if st.button("New Conversation", type="primary"):
        controller = _get_controller()
        conv = controller.start_conversation()
        st.session_state["conversation_id"] = (
            conv.conversation_id
        )
        st.session_state["messages"] = []
        st.session_state["active_comment_for"] = None
        st.rerun()

    if st.session_state["conversation_id"] is None:
        st.info(
            "Click **New Conversation** to start"
            " chatting."
        )
        return

    for entry in st.session_state["messages"]:
        render_message(
            role=entry["role"],
            content=entry["content"],
            message_id=entry.get("message_id"),
            message_context=entry.get(
                "message_context"
            ),
            datetime=entry.get("datetime"),
        )

    user_input = st.chat_input(
        "Ask a business question..."
    )
    if user_input:
        controller = _get_controller()
        history = [
            {
                "role": e["role"],
                "content": e["content"],
            }
            for e in st.session_state["messages"]
        ]

        user_msg, llm_msg = controller.send_message(
            st.session_state["conversation_id"],
            user_input,
            history,
        )

        st.session_state["messages"].append({
            "role": "user",
            "content": user_msg.content,
            "message_id": user_msg.message_id,
            "datetime": user_msg.datetime,
        })
        st.session_state["messages"].append({
            "role": "assistant",
            "content": llm_msg.content,
            "message_id": llm_msg.message_id,
            "message_context": llm_msg.message_context,
            "datetime": llm_msg.datetime,
        })
        st.rerun()
