
# FILE: src/data_loader.py
# -*- coding: utf-8 -*-
"""
This module is responsible for loading data for the analysis scripts.
It specifically reads the CLEANED data from the `data/processed` directory
and retrieves the list of available assets from the master config file.
"""
import pandas as pd
import os
import yaml
from pathlib import Path

def load_asset_data(processed_data_path, asset_name):
    """Loads CLEANED asset data for a specific asset."""
    input_file_path = processed_data_path / asset_name / f"{asset_name}.csv"
    
    if not os.path.exists(input_file_path):
        print(f"ERROR: Processed data file not found at {input_file_path}")
        print("       Please run the data acquisition (1) and cleaning (2) pipelines first.")
        return None

    try:
        df = pd.read_csv(input_file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values(by='Date', inplace=True)
        return df
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during data loading for {asset_name}: {e}")
        return None

def get_available_assets_from_config(config_path):
    """Retrieves the list of available assets from the master config."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        # Extract just the 'user_name' from each dictionary in the assets list
        return [asset['user_name'] for asset in config.get('assets', [])]
    except Exception as e:
        print(f"ERROR: Could not read assets from config file {config_path}: {e}")
        return []
