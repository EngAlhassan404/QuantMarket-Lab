# -*- coding: utf-8 -*-
"""
This module provides common utility functions that are used across the
platform, such as path management, date filtering, and directory setup.
Keeping these here prevents code duplication.
"""
import os
import pandas as pd
from pathlib import Path

def get_project_root():
    """Returns the absolute path to the project's root directory."""
    # This assumes utils.py is in src/, so we need to go up one level.
    return Path(__file__).parent.parent

def get_period_label(start_date, end_date):
    """Creates a standardized, file-safe text label for a time period."""
    # Convert to pandas Timestamps to safely use strftime
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date)
    
    start_str = start_ts.strftime('%Y%m%d') if pd.notna(start_ts) else 'Start'
    end_str = end_ts.strftime('%Y%m%d') if pd.notna(end_ts) else 'End'
    return f"{start_str}_to_{end_str}"

def filter_data_by_date(df, start_date, end_date):
    """
    Filters a DataFrame based on a start and end date.
    This function now robustly handles different date-like input types.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # --- FIX FOR TypeError ---
    # Convert start_date and end_date to pandas Timestamps before comparison.
    # This ensures that we are comparing the same data types (datetime64[ns]).
    start_ts = pd.to_datetime(start_date) if start_date else df['Date'].min()
    end_ts = pd.to_datetime(end_date) if end_date else df['Date'].max()

    # Apply the date filter using the converted timestamps
    mask = (df['Date'] >= start_ts) & (df['Date'] <= end_ts)
    return df.loc[mask].copy()

def setup_output_directory(root_results_dir, asset_name, period_label):
    """Creates and returns the path for an analysis run's output directory."""
    path = root_results_dir / asset_name / period_label
    os.makedirs(path, exist_ok=True)
    return path
