# -*- coding: utf-8 -*-
"""
==============================================================================
# QuantMarket-Lab - Step 2: Automated Data Cleaning Pipeline
#
# Purpose:
# This script reads raw data from the `data/raw` directory, performs a series
# of cleaning and validation steps, and saves the standardized, analysis-ready
# data to the `data/processed` directory.
#
# Role in Workflow:
# This is the crucial quality assurance gate. It ensures that all subsequent
# analysis is performed on a reliable and consistent dataset, free from common
# data issues like duplicates, invalid values, or incorrect formats.
==============================================================================
"""
import pandas as pd
import numpy as np
import yaml
import os
from pathlib import Path

def get_project_root():
    """Returns the absolute path to the project's root directory."""
    return Path(__file__).parent

def load_config():
    """Loads the master configuration file from the `configs` directory."""
    root = get_project_root()
    config_path = root / 'configs' / 'master_config.yml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def clean_and_validate_data(df, asset_name):
    """Performs all cleaning and validation steps on a given DataFrame."""
    print(f"\n--- Starting Cleaning & Validation for: {asset_name} ---")
    print(f"Initial raw rows to process: {len(df)}")
    
    # Step 1: Process and validate the 'Date' column
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    initial_rows = len(df)
    df.dropna(subset=['Date'], inplace=True)
    if len(df) < initial_rows:
        print(f"  - Removed {initial_rows - len(df)} rows due to invalid date format.")

    # Step 2: Remove duplicate entries based on the timestamp
    initial_rows = len(df)
    df.drop_duplicates(subset=['Date'], keep='first', inplace=True)
    if len(df) < initial_rows:
        print(f"  - Removed {initial_rows - len(df)} rows with duplicate timestamps.")

    # Step 3: Ensure all price columns are numeric and handle errors
    price_cols = ['Open', 'High', 'Low', 'Close']
    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Step 4: Drop any rows with missing or zero values in price columns
    initial_rows = len(df)
    df.dropna(subset=price_cols, inplace=True)
    df = df[(df[price_cols] != 0).all(axis=1)]
    if len(df) < initial_rows:
        print(f"  - Removed {initial_rows - len(df)} rows with invalid (NaN or zero) price values.")
    
    # Step 5: Engineer the primary 'Direction' feature
    df['Direction'] = "Break Even"
    df.loc[df['Close'] > df['Open'], 'Direction'] = 'UP'
    df.loc[df['Close'] < df['Open'], 'Direction'] = 'DOWN'
    print("  - 'Direction' column created/updated successfully.")

    # Step 6: Select and reorder columns to a standard format
    final_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Direction']
    df_final = df[[col for col in final_columns if col in df.columns]]
    
    # Final sort and index reset
    return df_final.sort_values(by='Date').reset_index(drop=True)

if __name__ == "__main__":
    config = load_config()
    PROJECT_ROOT = get_project_root()
    RAW_DATA_ROOT = PROJECT_ROOT / 'data' / 'raw'
    PROCESSED_DATA_ROOT = PROJECT_ROOT / 'data' / 'processed'
    
    print(f"--- Running: Automated Data Cleaning Pipeline ---")
    print(f"   (Reading from: {RAW_DATA_ROOT})")
    print(f"   (Saving to: {PROCESSED_DATA_ROOT})")

    # Iterate through all configured assets and clean them
    for asset_config in config['assets']:
        asset_name = asset_config["user_name"]
        
        input_filepath = RAW_DATA_ROOT / asset_name / f"{asset_name}.csv"
        output_filepath = PROCESSED_DATA_ROOT / asset_name / f"{asset_name}.csv"

        print("\n" + "#"*60)
        print(f"Processing Asset: {asset_name}")
        print("#"*60)
        print(f"  - Input file: {input_filepath}")

        try:
            df_raw = pd.read_csv(input_filepath)
        except FileNotFoundError:
            print(f"  - ❌ ERROR: Raw input file not found. Skipping. Run acquisition script first.")
            continue
            
        # Apply the cleaning and validation process
        df_clean = clean_and_validate_data(df_raw, asset_name)

        # Save the final clean file to the 'processed' directory
        if not df_clean.empty:
            os.makedirs(output_filepath.parent, exist_ok=True)
            df_clean.to_csv(output_filepath, index=False)
            print("\n--- ✅ SUCCESS! ---")
            print(f"Clean file for {asset_name} saved successfully.")
            print(f"  - Final row count: {len(df_clean)}")
            print(f"  - Output location: {output_filepath}")
        else:
            print("  - ❌ ERROR: Processing resulted in an empty dataset. No file was saved.")
            
    print("\n\n" + "="*80)
    print("Data Cleaning Pipeline Finished.")
    print("="*80)
