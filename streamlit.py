import importlib
import pathlib
from collections import defaultdict

import streamlit as st

from services import get_llm_service
from controllers.chat_controller import ChatController

EXCLUDED_STEMS = {"__init__", "_template"}


def _load_page_modules() -> list:
    pages_dir = pathlib.Path(__file__).parent / "pages"
    modules = []
    for filepath in sorted(pages_dir.glob("*.py")):
        if filepath.stem in EXCLUDED_STEMS:
            continue
        mod = importlib.import_module(f"pages.{filepath.stem}")
        modules.append(mod)
    modules.sort(key=lambda m: getattr(m, "PRIORITY", 999))
    return modules


def _build_controller() -> ChatController:
    return ChatController(chat_service=get_llm_service())


if "controller" not in st.session_state:
    st.session_state["controller"] = _build_controller()

modules = _load_page_modules()

sections: dict[str, list] = defaultdict(list)
for mod in modules:
    section = getattr(mod, "SECTION_NAME", "Main")
    page = st.Page(
        mod.build_page,
        title=getattr(mod, "PAGE_NAME", mod.__name__),
        url_path=getattr(mod, "URL_PATH", mod.__name__),
    )
    sections[section].append(page)

nav = st.navigation(dict(sections))
nav.run()
