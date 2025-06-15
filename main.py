import streamlit as st
from auth import show_auth_page

# Configure the Streamlit page
st.set_page_config(
    page_title="CSV Analyzer - Login",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "llama"

# Sidebar for model selection
with st.sidebar:
    st.title("Model Selection")
    st.selectbox(
        "Choose a model for analysis:",
        options=["llama", "gpt4o", "sarvam-m"],
        key="selected_model",
    )


def main():
    if not st.session_state.get("password_correct", False):
        show_auth_page()
    else:
        # Redirect to home page
        st.switch_page("pages/1_Home.py")


if __name__ == "__main__":
    main()
