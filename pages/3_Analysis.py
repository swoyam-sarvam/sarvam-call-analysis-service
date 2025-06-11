import streamlit as st
import pandas as pd  # type: ignore
import asyncio
import json
from typing import Dict, List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from call_analysis import analyze_transcript_with_config

# Configure the page
st.set_page_config(
    page_title="CSV Analyzer - Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Check if user is authenticated
if not st.session_state.get("password_correct", False):
    st.switch_page("main.py")

# Check if required data is available
if not hasattr(st.session_state, "uploaded_df") or not hasattr(
    st.session_state, "config_data"
):
    st.error(
        "Missing required data. Please upload a CSV file and configure analysis settings."
    )
    st.stop()


async def analyze_transcript_batch(
    transcripts: List[str],
    config: Dict[str, str],
    semaphore: asyncio.Semaphore,
    progress_callback=None,
):
    """
    Process transcripts in batches with semaphore control
    """
    results = []

    async def process_single_transcript(idx: int, transcript: str):
        async with semaphore:
            try:
                result = await analyze_transcript_with_config(transcript, config)
                if progress_callback:
                    progress_callback(idx, result)
                return idx, result
            except Exception as e:
                error_result = {key: "error" for key in config.keys()}
                if progress_callback:
                    progress_callback(idx, error_result)
                return idx, error_result

    # Create tasks for all transcripts
    tasks = [
        process_single_transcript(idx, transcript)
        for idx, transcript in enumerate(transcripts)
    ]

    # Process all tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results


def show_analysis_page():
    st.title("📊 Call Analysis Results")
    st.markdown("Processing transcripts with the configured analysis parameters...")

    # Get data from session state
    df = st.session_state.uploaded_df
    config = st.session_state.config_data

    # Display basic info
    st.subheader("Analysis Overview")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Transcripts", len(df))

    with col2:
        st.metric("Analysis Parameters", len(config))

    with col3:
        st.metric("Concurrent Tasks", 10)

    # Create results dataframe structure
    result_columns = ["Interaction ID"] + list(config.keys())
    results_df = pd.DataFrame(index=range(len(df)), columns=result_columns)
    results_df["Interaction ID"] = df["Interaction ID"].values

    # Initialize all analysis columns with "Processing..."
    for col in config.keys():
        results_df[col] = "🔄"

    # Create placeholder for the results table
    results_placeholder = st.empty()

    # Display initial table with spinners
    results_placeholder.dataframe(results_df, use_container_width=True)

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    completed_count = 0

    def update_progress(idx: int, result: Dict[str, str]):
        nonlocal completed_count
        completed_count += 1

        # Update the results dataframe
        for key, value in result.items():
            if key in results_df.columns:
                # Use emojis for better visual feedback
                display_value = (
                    "🔴"
                    if value.lower() == "yes"
                    else "💚" if value.lower() == "no" else "⚠️"
                )
                results_df.loc[idx, key] = display_value

        # Update progress
        progress = completed_count / len(df)
        progress_bar.progress(progress)
        status_text.text(
            f"Processed {completed_count}/{len(df)} transcripts ({progress:.1%})"
        )

        # Update the displayed table
        results_placeholder.dataframe(results_df, use_container_width=True)

    # Start analysis button
    if st.button("🚀 Start Analysis", use_container_width=True):
        status_text.text("Starting analysis...")

        # Create semaphore for limiting concurrent tasks
        semaphore = asyncio.Semaphore(10)

        # Get transcripts
        transcripts = df["Transcript"].tolist()

        try:
            # Run the async analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            results = loop.run_until_complete(
                analyze_transcript_batch(
                    transcripts, config, semaphore, update_progress
                )
            )

            loop.close()

            # Final update
            status_text.text("✅ Analysis completed!")
            st.success("All transcripts have been analyzed successfully!")

            # Store results in session state for potential export
            st.session_state.analysis_results = results_df

            # Add export button
            if st.button("📥 Export Results", use_container_width=True):
                csv_data = results_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="analysis_results.csv",
                    mime="text/csv",
                )

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            status_text.text("❌ Analysis failed!")

    # Show configuration details in expander
    with st.expander("📋 Configuration Details"):
        for key, value in config.items():
            st.write(f"**{key}**: {value}")


# Add navigation in sidebar
with st.sidebar:
    st.markdown("### Navigation")

    if st.button("🏠 Back to Home"):
        st.switch_page("pages/1_Home.py")

    if st.button("⚙️ Back to Config"):
        st.switch_page("pages/2_Config.py")

    if st.button("🚪 Logout"):
        st.session_state.password_correct = False
        st.switch_page("main.py")

    # Show analysis stats if available
    if hasattr(st.session_state, "analysis_results"):
        st.markdown("### Analysis Stats")
        analysis_df = st.session_state.analysis_results

        for col in st.session_state.config_data.keys():
            if col in analysis_df.columns:
                yes_count = (analysis_df[col] == "✅ Yes").sum()
                no_count = (analysis_df[col] == "❌ No").sum()
                error_count = (analysis_df[col] == "⚠️ Error").sum()

                st.write(f"**{col}**:")
                st.write(f"  ✅ Yes: {yes_count}")
                st.write(f"  ❌ No: {no_count}")
                if error_count > 0:
                    st.write(f"  ⚠️ Errors: {error_count}")


if __name__ == "__main__":
    show_analysis_page()
