import streamlit as st

PAGE_NAME = "Chat"
SECTION_NAME = "Main"
URL_PATH = "chat"
PRIORITY = 1


def _get_controller():
    return st.session_state["controller"]


def _render_feedback_row(message_id: int):
    controller = _get_controller()
    feedback = st.session_state.get(f"feedback_{message_id}", {})

    if feedback.get("submitted"):
        sentiment = "👍" if feedback["positive"] else "👎"
        st.caption(f"Your feedback: {sentiment} — {feedback['comment']}")
        return

    st.info("Feedback requires a rating and a comment.", icon="ℹ️")

    pending = st.session_state.get(f"pending_sentiment_{message_id}")

    col_up, col_down, _ = st.columns([1, 1, 9])
    with col_up:
        if st.button("👍", key=f"up_{message_id}", type="primary" if pending is True else "secondary"):
            st.session_state[f"pending_sentiment_{message_id}"] = True
            st.rerun()
    with col_down:
        if st.button("👎", key=f"down_{message_id}", type="primary" if pending is False else "secondary"):
            st.session_state[f"pending_sentiment_{message_id}"] = False
            st.rerun()

    if pending is not None:
        with st.form(key=f"feedback_form_{message_id}", clear_on_submit=False):
            text = st.text_area("Add a comment to complete your feedback")
            if st.form_submit_button("Submit feedback"):
                if not text.strip():
                    st.warning("A comment is required.")
                else:
                    controller.submit_feedback(message_id, positive_feedback=pending, comment=text.strip())
                    st.session_state[f"feedback_{message_id}"] = {
                        "submitted": True,
                        "positive": pending,
                        "comment": text.strip(),
                    }
                    del st.session_state[f"pending_sentiment_{message_id}"]
                    st.rerun()


def build_page():
    st.title("Business Chat Assistant")

    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = None
        st.session_state["messages"] = []

    if st.button("New Conversation", type="primary"):
        controller = _get_controller()
        conv = controller.start_conversation()
        st.session_state["conversation_id"] = conv.conversation_id
        st.session_state["messages"] = []
        st.session_state["active_comment_for"] = None
        st.rerun()

    if st.session_state["conversation_id"] is None:
        st.info("Click **New Conversation** to start chatting.")
        return

    for entry in st.session_state["messages"]:
        role = entry["role"]
        content = entry["content"]
        message_id = entry.get("message_id")

        with st.chat_message(role):
            st.markdown(content)

        if role == "assistant" and message_id:
            _render_feedback_row(message_id)

    user_input = st.chat_input("Ask a business question...")
    if user_input:
        controller = _get_controller()
        history = [
            {"role": e["role"], "content": e["content"]}
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
        })
        st.session_state["messages"].append({
            "role": "assistant",
            "content": llm_msg.content,
            "message_id": llm_msg.message_id,
        })
        st.rerun()
