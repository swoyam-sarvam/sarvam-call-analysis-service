import streamlit as st
import pandas as pd  # type: ignore
import json

# Configure the page
st.set_page_config(
    page_title="CSV Analyzer - Config",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Check if user is authenticated
if not st.session_state.get("password_correct", False):
    st.switch_page("main.py")

# Default configuration
DEFAULT_CONFIG = {
    "Loop": "Identify any instances where the assistant repeats the same message content 3 or more times consecutively, excluding 'No Content' responses. This indicates a potential conversation loop., Return yes if loop exists",
    "OffTopic": "Detect when the assistant provides responses that are contextually inappropriate, particularly focusing on cases where variables are mentioned out of context or the conversation drastically deviates from the expected flow. return yes if the assistant goes off topic or else no",
    "Date": "Validate that all date variables strictly follow the DD/Mon/YYYY format, where Mon must be a three-letter abbreviation (e.g., 15/Jan/2024). Flag any deviations from this format. Flag yes if it is not in the given format, no if it is in the format",
    "Name": "Ensure all names are properly capitalized in Title Case format (e.g., 'John Smith' not 'JOHN SMITH' or 'john smith'). Flag any names that don't follow this convention. Reply yes if its not in title case or else no",
    "Currency": "Verify that all currency amounts use proper Indian number formatting with appropriate comma placement (e.g., 1,00,000 for one lakh, 25,000 for twenty-five thousand). Flag amounts missing commas or using incorrect comma placement. reply yes if currency is not in indian format or else return no",
    "PIN": "Identify any PIN codes that incorrectly contain commas in their format. PIN codes should be continuous 6-digit numbers without any separators. Return yes if PIN has commas or else return no",
}


def initialize_config():
    """Initialize configuration in session state if not present"""
    if "config_data" not in st.session_state:
        st.session_state.config_data = DEFAULT_CONFIG.copy()


def show_config_page():
    st.title("Call Analysis Configuration")
    st.markdown(
        "Manage your analysis configuration below. You can delete or add new flags as needed."
    )

    initialize_config()

    # Convert config to DataFrame for editing
    config_df = pd.DataFrame(
        list(st.session_state.config_data.items()), columns=["Key", "Value"]
    )

    # Display editable dataframe
    edited_df = st.data_editor(
        config_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Key": st.column_config.TextColumn(
                "Key", help="Configuration key name", max_chars=50, required=True
            ),
            "Value": st.column_config.TextColumn(
                "Value",
                help="Configuration description/value",
                max_chars=500,
                required=True,
            ),
        },
        key="config_editor",
    )

    # Save configuration and proceed to analysis
    if st.button("🔄 Process Calls", use_container_width=True):
        # Validate configuration
        if (
            edited_df.empty
            or edited_df["Key"].isna().any()
            or edited_df["Value"].isna().any()
        ):
            st.error(
                "Please ensure all configuration entries have both Key and Value filled."
            )
        else:
            st.session_state.config_data = dict(
                zip(edited_df["Key"], edited_df["Value"])
            )
            st.success("Configuration saved successfully!")
            # Redirect to analysis page
            st.switch_page("pages/3_Analysis.py")


# Add navigation in sidebar
with st.sidebar:
    st.markdown("### Navigation")
    if st.button("🏠 Back to Home"):
        st.switch_page("pages/1_Home.py")

    # Show analysis button if config is ready
    if hasattr(st.session_state, "config_data") and st.session_state.config_data:
        if st.button("🔍 Go to Analysis"):
            st.switch_page("pages/3_Analysis.py")

    if st.button("🚪 Logout"):
        st.session_state.password_correct = False
        st.switch_page("main.py")

if __name__ == "__main__":
    show_config_page()
