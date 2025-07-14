# -*- coding: utf-8 -*-
"""
==============================================================================
# QuantMarket-Lab - Step 3: Analysis Engine (CLI)
#
# Purpose:
# This script is the Command-Line Interface (CLI) for running the core
# statistical analysis on the cleaned data. It allows for automated and
# scriptable generation of reports and visualizations.
#
# Role in Workflow:
# This is the primary tool for batch processing and reproducing the specific
# case studies outlined in the project documentation. It reads from the
# `data/processed` directory and saves output to the `results` directory.
==============================================================================
"""
import argparse
import pandas as pd
from pathlib import Path

# Since this script is in the root, we can directly import from 'src'
from src.utils import filter_data_by_date, setup_output_directory, get_period_label
from src.data_loader import load_asset_data
from src.analysis_engine import run_analysis, calculate_day_of_week_distribution
from src.visualization import generate_plots
from src.reporting import save_summary_report, save_processed_data_to_csv

def get_project_root():
    """Returns the absolute path to the project's root directory."""
    return Path(__file__).parent

def main_cli():
    """The main function to parse arguments and run the CLI analysis."""
    # Setup argument parser to accept command-line inputs
    parser = argparse.ArgumentParser(
        description="QuantMarket-Lab Analysis CLI",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--asset', required=True, type=str, help='Specify a single asset to analyze (e.g., GOLD).')
    parser.add_argument('--start_date', type=str, help='Analysis start date in YYYY-MM-DD format.')
    parser.add_argument('--end_date', type=str, help='Analysis end date in YYYY-MM-DD format.')
    args = parser.parse_args()

    # Define project paths
    PROCESSED_DATA_DIR = get_project_root() / 'data' / 'processed'
    RESULTS_DIR = get_project_root() / 'results'
    asset = args.asset
    
    print(f"\n{'='*20} Starting Analysis for: {asset.upper()} {'='*20}")
    
    # Load the clean data for the specified asset
    df_full = load_asset_data(PROCESSED_DATA_DIR, asset)
    if df_full is None:
        return # Error message is handled inside the loader
        
    # Convert date strings from arguments to datetime objects
    start_date_obj = pd.to_datetime(args.start_date) if args.start_date else None
    end_date_obj = pd.to_datetime(args.end_date) if args.end_date else None
    
    # Filter the data for the specified period
    df_period = filter_data_by_date(df_full, start_date_obj, end_date_obj)
    if df_period.empty:
        print(f"No data available for {asset} in the specified period. Skipping.")
        return

    # Prepare output directory
    period_label = get_period_label(start_date_obj, end_date_obj)
    output_dir = setup_output_directory(RESULTS_DIR, asset, period_label)
    print(f"Output will be saved to: {output_dir}")

    # Run the core analysis and generate outputs
    df_analyzed, summary_stats = run_analysis(df_period)
    dow_dist = calculate_day_of_week_distribution(df_analyzed)
    
    save_summary_report(summary_stats, dow_dist, output_dir, asset, period_label)
    save_processed_data_to_csv(df_analyzed, output_dir, asset, period_label)
    generate_plots(df_analyzed, dow_dist, output_dir, asset, period_label)
    
    print(f"--- Analysis for {asset} completed successfully! ---")

if __name__ == "__main__":
    main_cli()
