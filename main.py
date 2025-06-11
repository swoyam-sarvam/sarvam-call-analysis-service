import streamlit as st
from auth import show_auth_page

# Configure the Streamlit page
st.set_page_config(
    page_title="CSV Analyzer - Login",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide the sidebar menu during login
st.markdown(
    """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False


def main():
    if not st.session_state.get("password_correct", False):
        show_auth_page()
    else:
        # Redirect to home page
        st.switch_page("pages/1_Home.py")


if __name__ == "__main__":
    main()
