import importlib
import pathlib
from collections import defaultdict
from dataclasses import dataclass, field
from types import ModuleType
from typing import Callable, Dict, List, Optional, Set

import streamlit as st

EXCLUDED_STEMS = {"__init__", "_template"}


@dataclass
class PageInfo:
    callable: Callable[[], None]
    section: str
    title: str
    url_path: str
    page: st.Page
    required_roles: Set[str] = field(
        default_factory=set
    )


def _load_page_modules() -> List[ModuleType]:
    pages_dir = pathlib.Path(__file__).parent
    modules = []
    for filepath in sorted(pages_dir.glob("*.py")):
        if filepath.stem in EXCLUDED_STEMS:
            continue
        modules.append(
            importlib.import_module(
                f"pages.{filepath.stem}"
            )
        )
    modules.sort(
        key=lambda m: getattr(m, "PRIORITY", 999)
    )
    return modules


def _module_to_page_info(mod: ModuleType) -> PageInfo:
    build_page: Callable[[], None] = mod.build_page
    title = getattr(mod, "PAGE_NAME", mod.__name__)
    url_path = getattr(mod, "URL_PATH", mod.__name__)
    return PageInfo(
        callable=build_page,
        section=getattr(mod, "SECTION_NAME", "Main"),
        title=title,
        url_path=url_path,
        required_roles=set(
            getattr(mod, "REQUIRED_ROLES", set())
        ),
        page=st.Page(
            build_page, title=title, url_path=url_path
        ),
    )


def _page_infos(
    user_roles: Optional[Set[str]] = None,
) -> List[PageInfo]:
    infos = [
        _module_to_page_info(mod)
        for mod in _load_page_modules()
    ]
    if user_roles is None:
        return infos
    return [
        info for info in infos
        if not info.required_roles
        or info.required_roles & user_roles
    ]


def load_page_sections(
    user_roles: Optional[Set[str]] = None,
) -> Dict[str, List[st.Page]]:
    sections: Dict[str, List[st.Page]] = defaultdict(
        list
    )
    for info in _page_infos(user_roles):
        sections[info.section].append(info.page)
    return dict(sections)


def load_page_urls() -> Dict[str, st.Page]:
    return {
        info.url_path: info.page
        for info in _page_infos()
    }
