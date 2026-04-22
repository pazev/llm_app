"""
Page template — copy this file to create a new page.

Each page module must define the four module-level variables
below and implement the build_page() function.

PRIORITY: lower number = higher priority = shown first in
          the navigation. If two pages share the same
          priority, the first one found is shown first.
"""

PAGE_NAME = "Template Page"
SECTION_NAME = "Main"
URL_PATH = "template"
PRIORITY = 100
HIDE_IF_LOGGED_IN = False


def build_page():
    """Build the Streamlit page UI. Called by the navigation
    framework."""
    import streamlit as st
    st.title(PAGE_NAME)
    st.write("Replace this with your page content.")
