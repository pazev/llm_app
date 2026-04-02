import streamlit as st

from pages import load_page_urls

PAGE_NAME = "Conversations"
SECTION_NAME = "Main"
URL_PATH = "conversations"
PRIORITY = 2


def _get_controller():
    return st.session_state["controller"]


def _render_feedback(message_id: int, existing_feedback):
    controller = _get_controller()

    if (
        f"feedback_{message_id}" not in st.session_state
        and existing_feedback is not None
    ):
        st.session_state[f"feedback_{message_id}"] = {
            "submitted": True,
            "positive": existing_feedback.positive_feedback,
            "comment": existing_feedback.comment,
        }

    feedback = st.session_state.get(
        f"feedback_{message_id}", {}
    )

    if feedback.get("submitted"):
        sentiment = "👍" if feedback["positive"] else "👎"
        st.caption(
            f"Feedback: {sentiment} — {feedback['comment']}"
        )
        return

    st.info(
        "Feedback requires a rating and a comment.",
        icon="ℹ️",
    )

    pending = st.session_state.get(
        f"pending_sentiment_{message_id}"
    )

    col_up, col_down, _ = st.columns([1, 1, 9])
    with col_up:
        if st.button(
            "👍",
            key=f"up_{message_id}",
            type="primary" if pending is True else "secondary",
        ):
            st.session_state[
                f"pending_sentiment_{message_id}"
            ] = True
            st.rerun()
    with col_down:
        if st.button(
            "👎",
            key=f"down_{message_id}",
            type=(
                "primary" if pending is False else "secondary"
            ),
        ):
            st.session_state[
                f"pending_sentiment_{message_id}"
            ] = False
            st.rerun()

    if pending is not None:
        with st.form(
            key=f"feedback_form_{message_id}",
            clear_on_submit=False,
        ):
            text = st.text_area(
                "Add a comment to complete your feedback"
            )
            if st.form_submit_button("Submit feedback"):
                if not text.strip():
                    st.warning("A comment is required.")
                else:
                    controller.submit_feedback(
                        message_id,
                        positive_feedback=pending,
                        comment=text.strip(),
                    )
                    st.session_state[
                        f"feedback_{message_id}"
                    ] = {
                        "submitted": True,
                        "positive": pending,
                        "comment": text.strip(),
                    }
                    del st.session_state[
                        f"pending_sentiment_{message_id}"
                    ]
                    st.rerun()


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
            title = (
                conv.title
                or f"Conversation #{conv.conversation_id}"
            )
            created = conv.datetime_start.strftime(
                "%Y-%m-%d %H:%M"
            )
            with st.container(border=True):
                st.markdown(f"**{title}**")
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
                with st.chat_message(role):
                    st.markdown(msg.content)
                    st.caption(
                        msg.datetime.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )

                if msg.sender == "llm":
                    _render_feedback(
                        msg.message_id,
                        feedbacks.get(msg.message_id),
                    )
