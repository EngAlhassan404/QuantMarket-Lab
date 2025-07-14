# -*- coding: utf-8 -*-
"""
==============================================================================
# QuantMarket-Lab - Step 4: Analysis Laboratory (GUI)
#
# Purpose:
# This script launches the Streamlit-based Graphical User Interface (GUI),
# providing an interactive, web-based "laboratory" for exploring the data
# and analysis results visually.
#
# v2 Enhancements:
# - Fixed TypeError by correctly handling date/datetime object comparisons.
# - Implemented "smart" date inputs: The date range now dynamically defaults
#   to the available range of the selected asset's data.
==============================================================================
"""
import streamlit as st
import pandas as pd
import datetime
from pathlib import Path

# Since this script is in the root, we can directly import from 'src'
from src.utils import filter_data_by_date, setup_output_directory, get_period_label
from src.data_loader import load_asset_data, get_available_assets_from_config
from src.analysis_engine import run_analysis, calculate_day_of_week_distribution
from src.visualization import generate_plots

def get_project_root():
    """Returns the absolute path to the project's root directory."""
    return Path(__file__).parent

# --- 1. Page Setup and Path Configuration ---
st.set_page_config(page_title="QuantMarket-Lab", layout="wide")
st.title("🔬 QuantMarket-Lab: Financial Direction Analysis")

# Define project paths
ROOT_DIR = get_project_root()
PROCESSED_DATA_DIR = ROOT_DIR / 'data' / 'processed'
CONFIG_PATH = ROOT_DIR / 'configs' / 'master_config.yml'
RESULTS_DIR = ROOT_DIR / 'results'

# --- 2. Sidebar for User Inputs ---
st.sidebar.header("Analysis Configuration")

# Populate asset dropdown from the master config file
available_assets = get_available_assets_from_config(CONFIG_PATH)
if not available_assets:
    st.sidebar.error("Could not load assets from `configs/master_config.yml`.")
    st.stop()

selected_asset = st.sidebar.selectbox("Select Asset", available_assets)

# --- SMART DATE INPUTS LOGIC ---
# Load the data for the selected asset first to determine the available date range.
# This makes the date pickers dynamic and user-friendly.
df_full = load_asset_data(PROCESSED_DATA_DIR, selected_asset)

if df_full is not None and not df_full.empty:
    # Determine the min and max dates from the loaded data
    min_date_available = df_full['Date'].min().date()
    max_date_available = df_full['Date'].max().date()

    # Set the default end date to today, but not exceeding the available data
    default_end_date = min(datetime.date.today(), max_date_available)

    # Display a helpful info message to the user
    st.sidebar.info(f"Data for {selected_asset} available from {min_date_available.strftime('%Y-%m-%d')} to {max_date_available.strftime('%Y-%m-%d')}.")

    # Create the date input widgets with smart defaults
    start_date = st.sidebar.date_input(
        "Start Date",
        value=min_date_available,       # Default to the earliest available date
        min_value=min_date_available,   # Set the lower bound
        max_value=max_date_available    # Set the upper bound
    )
    end_date = st.sidebar.date_input(
        "End Date",
        value=default_end_date,         # Default to today or the latest available date
        min_value=min_date_available,
        max_value=max_date_available
    )
else:
    # Fallback for when data is not available
    st.sidebar.warning(f"No data found for {selected_asset}. Please run the data pipelines.")
    # Create disabled date inputs
    start_date = st.sidebar.date_input("Start Date", disabled=True)
    end_date = st.sidebar.date_input("End Date", disabled=True)


analyze_button = st.sidebar.button("🔬 Run Analysis", type="primary")

# --- 3. Main Panel: Analysis and Display Logic ---
if analyze_button:
    # Proceed only if data was loaded successfully
    if df_full is not None and not df_full.empty:
        # Basic validation
        if start_date > end_date:
            st.error("Error: Start date must be before end date.")
        else:
            # Show a spinner while processing
            with st.spinner(f"Analyzing {selected_asset}..."):
                # Filter data for the selected period
                # The conversion to handle the TypeError is now inside filter_data_by_date
                df_period = filter_data_by_date(df_full, start_date, end_date)

                if df_period.empty:
                    st.warning(f"No data available for {selected_asset} in the selected period.")
                    st.stop()

                # Prepare output directory
                period_label = get_period_label(start_date, end_date)
                output_dir = setup_output_directory(RESULTS_DIR, selected_asset, period_label)

                # Run the analysis and generate plots
                df_analyzed, summary_stats = run_analysis(df_period)
                dow_dist = calculate_day_of_week_distribution(df_analyzed)
                plot_paths = generate_plots(df_analyzed, dow_dist, output_dir, selected_asset, period_label)
                
                st.success(f"Analysis complete for {selected_asset}!")

                # --- Display Results ---
                st.header(f"Results for {selected_asset}")
                st.subheader(f"Period: {summary_stats['actual_start_date']} to {summary_stats['actual_end_date']}")

                # Key metrics in columns
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Trading Days", summary_stats['total_days'])
                col2.metric("UP Days", f"{summary_stats['up_days']} ({summary_stats['up_pct']:.1f}%)")
                col3.metric("DOWN Days", f"{summary_stats['down_days']} ({summary_stats['down_pct']:.1f}%)")
                
                # Display all generated plots
                st.subheader("Visualizations")
                st.image(str(plot_paths['overall_dist_pie']), caption="Overall Direction Distribution")
                st.image(str(plot_paths['cumulative_days']), caption="Cumulative Days Trend")
                st.image(str(plot_paths['cumulative_points']), caption="Cumulative Points Trend")
                st.image(str(plot_paths['dow_dist_grouped']), caption="Day of Week Distribution")
    else:
        st.error(f"Cannot run analysis. Data for {selected_asset} is not available.")
