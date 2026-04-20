import streamlit as st

from pages import load_page_urls
from pages.utils.message import render_message

PAGE_NAME = "Conversations"
SECTION_NAME = "Main"
URL_PATH = "conversations"
PRIORITY = 2


def _get_controller():
    return st.session_state["controller"]


def build_page():
    st.title("Conversations")

    controller = _get_controller()
    conversations = controller.list_conversations()

    if not conversations:
        st.info(
            "No conversations yet. Start one from the"
            " Chat page."
        )
        return

    selected_id = st.session_state.get(
        "conversations_selected_id"
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
                st.caption(
                    f"Messages: {conv.message_count}"
                    f" · Feedbacks: {conv.feedback_count}"
                )
                btn_col, resume_col = st.columns(2)
                with btn_col:
                    if st.button(
                        "View",
                        key=(
                            f"view_conv_"
                            f"{conv.conversation_id}"
                        ),
                        type=(
                            "primary"
                            if selected_id
                            == conv.conversation_id
                            else "secondary"
                        ),
                    ):
                        st.session_state[
                            "conversations_selected_id"
                        ] = conv.conversation_id
                        st.rerun()
                with resume_col:
                    if st.button(
                        "Resume",
                        key=(
                            f"resume_conv_"
                            f"{conv.conversation_id}"
                        ),
                    ):
                        new_conv, old_messages = (
                            controller.resume_conversation(
                                conv.conversation_id
                            )
                        )
                        st.session_state[
                            "conversation_id"
                        ] = new_conv.conversation_id
                        st.session_state["messages"] = [
                            {
                                "role": (
                                    "user"
                                    if m.sender == "user"
                                    else "assistant"
                                ),
                                "content": m.content,
                                "message_id": m.message_id,
                                "datetime": m.datetime,
                                **(
                                    {
                                        "message_context": (
                                            m.message_context
                                        )
                                    }
                                    if m.sender == "llm"
                                    else {}
                                ),
                            }
                            for m in old_messages
                        ]
                        st.switch_page(load_page_urls()["chat"])

    with col_right:
        if selected_id is None:
            st.info(
                "Select a conversation to view its messages."
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
