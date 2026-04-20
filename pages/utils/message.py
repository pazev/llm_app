"""
Shared message rendering utilities.

Used by both the chat and conversations pages
to ensure a consistent display of messages,
feedback, and context debug information.
"""

from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st


def render_feedback_row(
    message_id: int,
    existing_feedbacks=None,
):
    """Render thumbs feedback UI for an LLM message.

    ``existing_feedbacks`` is a list of
    FeedbackResponse objects (or None). When provided,
    the list is seeded into session state on first
    render so stored feedbacks appear immediately.
    Multiple feedbacks per message are supported.
    """
    st.markdown(
        """
        <style>
        [data-testid="stChatMessage"] .stButton > button {
            padding: 6px 6px !important;
            font-size: 0.75rem !important;
            line-height: 1 !important;
            min-height: 0 !important;
            width: fit-content !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    controller = st.session_state["controller"]
    list_key = f"feedbacks_{message_id}"
    pending_key = f"pending_sentiment_{message_id}"

    if (
        list_key not in st.session_state
        and existing_feedbacks
    ):
        st.session_state[list_key] = [
            {
                "positive": fb.positive_feedback,
                "comment": fb.comment,
                "datetime": fb.datetime,
            }
            for fb in existing_feedbacks
        ]

    for fb in st.session_state.get(list_key, []):
        sentiment = (
            "👍" if fb["positive"] else "👎"
        )
        dt = fb["datetime"]
        dt_str = (
            dt.strftime("%Y-%m-%d %H:%M:%S")
            if dt else ""
        )
        st.caption(
            f"{sentiment} {fb['comment']}"
            f" — {dt_str}"
        )

    pending = st.session_state.get(pending_key)

    col_up, col_down, _ = st.columns([1, 1, 9])
    with col_up:
        if st.button(
            "👍",
            key=f"up_{message_id}",
            type=(
                "primary" if pending is True
                else "secondary"
            ),
        ):
            if pending is True:
                del st.session_state[pending_key]
            else:
                st.session_state[pending_key] = True
            st.rerun()
    with col_down:
        if st.button(
            "👎",
            key=f"down_{message_id}",
            type=(
                "primary" if pending is False
                else "secondary"
            ),
        ):
            if pending is False:
                del st.session_state[pending_key]
            else:
                st.session_state[pending_key] = False
            st.rerun()

    if pending is not None:
        with st.form(
            key=f"feedback_form_{message_id}",
            clear_on_submit=False,
        ):
            text = st.text_area(
                "Comment",
                help=(
                    "A rating and a comment are"
                    " required to submit feedback."
                ),
            )
            if st.form_submit_button(
                "Submit feedback"
            ):
                if not text.strip():
                    st.warning(
                        "A comment is required."
                    )
                else:
                    result = controller.submit_feedback(
                        message_id,
                        positive_feedback=pending,
                        comment=text.strip(),
                    )
                    st.session_state.setdefault(
                        list_key, []
                    ).append({
                        "positive": pending,
                        "comment": text.strip(),
                        "datetime": result.datetime,
                    })
                    del st.session_state[pending_key]
                    st.rerun()


def render_context_debug(
    context: List[Dict],
    message_id: int,
):
    if not context:
        return
    count = len(context)
    plural = "s" if count != 1 else ""
    total = sum(
        msg.get("token_usage", 0) for msg in context
    )
    total_in = sum(
        msg.get("input_tokens", 0) for msg in context
    )
    total_out = sum(
        msg.get("output_tokens", 0) for msg in context
    )
    with st.expander(
        f"🔍 Context ({count} message{plural},"
        f" {total} tokens"
        f" — in {total_in}, out {total_out})"
    ):
        for i, msg in enumerate(context):
            tok = msg.get("token_usage", 0)
            tok_in = msg.get("input_tokens", 0)
            tok_out = msg.get("output_tokens", 0)
            label = (
                f"{i + 1}."
                f" {msg.get('type', 'Message')}:"
                f" {tok} tokens"
                f" (in {tok_in} / out {tok_out})"
            )
            if msg.get("tool_calls"):
                tools = ", ".join(
                    tc["name"]
                    for tc in msg["tool_calls"]
                )
                label += f" → {tools}"
            with st.expander(label, expanded=False):
                if msg.get("content"):
                    st.markdown("**Content:**")
                    st.code(
                        msg["content"], language=None
                    )
                if msg.get("tool_calls"):
                    st.markdown("**Tool calls:**")
                    st.json(msg["tool_calls"])
                if msg.get("additional_kwargs"):
                    st.markdown(
                        "**Additional kwargs:**"
                    )
                    st.json(msg["additional_kwargs"])
                if msg.get("response_metadata"):
                    st.markdown(
                        "**Response metadata:**"
                    )
                    st.json(msg["response_metadata"])


def render_message(
    role: str,
    content: str,
    message_id: Optional[int] = None,
    message_context: Optional[List[Dict]] = None,
    existing_feedbacks=None,
    datetime: Optional[datetime] = None,
):
    """Render a single chat message with optional
    context debug and feedback row.

    Args:
        role: "user" or "assistant".
        content: Message text (markdown supported).
        message_id: DB id; required for feedback
            and context debug.
        message_context: LangChain context messages
            for the debug expander (assistant only).
        existing_feedbacks: List of
            FeedbackResponse from the DB, or None.
        datetime: When provided, shown as a caption
            inside the message bubble.
    """
    with st.chat_message(role):
        st.markdown(content)
        if datetime is not None:
            st.caption(
                datetime.strftime("%Y-%m-%d %H:%M:%S")
            )
        if role == "assistant" and message_id:
            render_context_debug(
                message_context or [], message_id
            )
            render_feedback_row(
                message_id, existing_feedbacks
            )
