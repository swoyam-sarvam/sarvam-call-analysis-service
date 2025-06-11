import os
import streamlit as st
from dotenv import load_dotenv


def check_password():
    """Returns `True` if the user had the correct password."""
    load_dotenv()  # Load environment variables from .env file

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"].strip() == os.getenv(
            "USERNAME", "admin"
        ) and st.session_state["password"] == os.getenv("PASSWORD", "admin123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
            del st.session_state["username"]  # Don't store the username.
            st.switch_page("pages/1_Home.py")
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input fields for username and password.
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password")
    st.button("Login", on_click=password_entered)

    if "password_correct" in st.session_state:
        if not st.session_state["password_correct"]:
            st.error("😕 Invalid username or password")

    return False


def show_auth_page():
    st.title("Login")
    st.markdown("Please enter your credentials to continue.")
    return check_password()
