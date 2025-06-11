import streamlit as st
import pandas as pd  # type: ignore

# Configure the page
st.set_page_config(
    page_title="CSV Analyzer - Home",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Check if user is authenticated
if not st.session_state.get("password_correct", False):
    st.switch_page("main.py")


def show_home_page():
    st.title("CSV File Upload")
    st.markdown("Upload your CSV file below for analysis.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file, low_memory=False, dtype=str)

            # Check for required columns
            required_columns = ["User Identifier", "Number of Messages", "Transcript"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                st.error(
                    f"Error: The following required columns are missing: {', '.join(missing_columns)}"
                )
                st.info(
                    "Please upload a CSV file with all the required columns: User Identifer, Number of Messages, Transcript"
                )
            else:
                # Display basic information about the dataset
                st.subheader("File Information")
                st.write(f"Number of Interactions: {df.shape[0]}")

                # Store the valid dataframe in session state
                st.session_state.uploaded_df = df

                # Show success message and configuration button
                st.success(
                    "✅ CSV format is correct! All required columns are present."
                )

                # Configuration button - only visible when CSV format is correct
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("⚙️ Configure Analysis", use_container_width=True):
                        st.switch_page("pages/2_Config.py")

                # Optional: Show column preview
                with st.expander("📋 Column Preview"):
                    for col in required_columns:
                        st.write(
                            f"**{col}**: {df[col].iloc[0] if len(df) > 0 else 'No data'}"
                        )

        except Exception as e:
            st.error(f"Error reading the file: {str(e)}")
    else:
        st.info("Please upload a CSV file to begin analysis.")


# Add logout button in sidebar
with st.sidebar:
    st.markdown("### Navigation")

    # Show additional navigation if CSV is loaded
    if hasattr(st.session_state, "uploaded_df"):
        if st.button("⚙️ Configuration"):
            st.switch_page("pages/2_Config.py")

    if st.button("🚪 Logout"):
        st.session_state.password_correct = False
        st.switch_page("main.py")

if __name__ == "__main__":
    show_home_page()
