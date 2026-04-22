import streamlit as st

from pages.utils.message import render_message

PAGE_NAME = "All Conversations"
SECTION_NAME = "Admin"
URL_PATH = "admin-conversations"
PRIORITY = 101
REQUIRED_ROLES = {"admin"}
HIDE_IF_LOGGED_IN = False


def _get_controller():
    return st.session_state["controller"]


def build_page():
    st.title("All Conversations")

    controller = _get_controller()
    conversations = controller.list_conversations()

    if not conversations:
        st.info("No conversations yet.")
        return

    selected_id = st.session_state.get(
        "admin_conversations_selected_id"
    )

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.subheader("History")
        for conv in conversations:
            created = conv.datetime_start.strftime(
                "%Y-%m-%d %H:%M"
            )
            with st.container(border=True):
                st.markdown(
                    f"**Conversation"
                    f" #{conv.conversation_id}**"
                )
                if conv.resumed_from_conversation_id:
                    st.caption(
                        "Resumed from Conversation"
                        f" #{conv.resumed_from_conversation_id}"
                    )
                st.caption(f"Created: {created}")
                if conv.username:
                    st.caption(f"User: {conv.username}")
                st.caption(
                    f"Messages: {conv.message_count}"
                    f" · Feedbacks: {conv.feedback_count}"
                )
                st.caption(
                    f"Tokens: {conv.token_usage}"
                    f" (in {conv.input_tokens}"
                    f" / out {conv.output_tokens})"
                )
                if st.button(
                    "View",
                    key=(
                        f"admin_view_conv_"
                        f"{conv.conversation_id}"
                    ),
                    type=(
                        "primary"
                        if selected_id == conv.conversation_id
                        else "secondary"
                    ),
                ):
                    st.session_state[
                        "admin_conversations_selected_id"
                    ] = conv.conversation_id
                    st.rerun()

    with col_right:
        if selected_id is None:
            st.info(
                "Select a conversation to view its"
                " messages."
            )
        else:
            messages = controller.get_conversation_messages(
                selected_id
            )
            feedbacks = (
                controller.get_conversation_feedbacks(
                    selected_id
                )
            )

            for msg in messages:
                role = (
                    "user"
                    if msg.sender == "user"
                    else "assistant"
                )
                render_message(
                    role=role,
                    content=msg.content,
                    message_id=msg.message_id,
                    message_context=getattr(
                        msg, "message_context", None
                    ),
                    existing_feedbacks=feedbacks.get(
                        msg.message_id
                    ),
                    datetime=msg.datetime,
                )
