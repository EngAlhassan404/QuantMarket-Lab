
# FILE: src/analysis_engine.py
# -*- coding: utf-8 -*-
"""
This is the core computational engine of the platform. It takes a clean
DataFrame and performs all the statistical calculations required for the
directional analysis, returning both the enriched data and a dictionary
of summary statistics.
"""
import pandas as pd
import numpy as np

def run_analysis(df, point_multiplier=10, point_decimals=2):
    """Performs statistical analysis on the provided DataFrame."""
    if df.empty:
        return pd.DataFrame(), {}

    df_analysis = df.copy()
    
    # Engineer Day_Name feature, needed for day-of-week analysis
    df_analysis['Day_Name'] = df_analysis['Date'].dt.day_name()

    # Calculate raw and scaled points
    df_analysis['Raw_Points'] = df_analysis['Close'] - df_analysis['Open']
    df_analysis['Points_Display'] = df_analysis['Raw_Points'] * point_multiplier

    # Calculate summary counts and percentages
    total_days = len(df_analysis)
    up_days = (df_analysis['Direction'] == 'UP').sum()
    down_days = (df_analysis['Direction'] == 'DOWN').sum()
    break_even_days = total_days - up_days - down_days

    # Calculate longest consecutive streaks for each direction
    df_analysis['streak_group'] = (df_analysis['Direction'] != df_analysis['Direction'].shift()).cumsum()
    streaks = df_analysis.groupby('streak_group')['Direction'].agg(['first', 'size'])
    
    longest_up_streak = streaks[streaks['first'] == 'UP']['size'].max()
    longest_down_streak = streaks[streaks['first'] == 'DOWN']['size'].max()
    longest_break_even_streak = streaks[streaks['first'] == 'Break Even']['size'].max()

    # Assemble all results into a structured dictionary
    summary_stats = {
        'total_days': total_days,
        'up_days': int(up_days),
        'down_days': int(down_days),
        'break_even_days': int(break_even_days),
        'up_pct': (up_days / total_days) * 100 if total_days > 0 else 0,
        'down_pct': (down_days / total_days) * 100 if total_days > 0 else 0,
        'break_even_pct': (break_even_days / total_days) * 100 if total_days > 0 else 0,
        'total_up_points_display': df_analysis.loc[df_analysis['Direction'] == 'UP', 'Points_Display'].sum(),
        'total_down_points_display': df_analysis.loc[df_analysis['Direction'] == 'DOWN', 'Points_Display'].abs().sum(),
        'net_points_display': df_analysis['Points_Display'].sum(),
        'longest_up_streak': 0 if pd.isna(longest_up_streak) else int(longest_up_streak),
        'longest_down_streak': 0 if pd.isna(longest_down_streak) else int(longest_down_streak),
        'longest_break_even_streak': 0 if pd.isna(longest_break_even_streak) else int(longest_break_even_streak),
        'point_multiplier': point_multiplier,
        'point_decimals': point_decimals,
        'actual_start_date': df_analysis['Date'].min().strftime('%Y-%m-%d'),
        'actual_end_date': df_analysis['Date'].max().strftime('%Y-%m-%d'),
    }
    return df_analysis, summary_stats

def calculate_day_of_week_distribution(df_analysis):
    """Calculates the distribution of directions across the days of the week."""
    if df_analysis.empty or 'Direction' not in df_analysis.columns:
        return pd.DataFrame()
        
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    directions_order = ['UP', 'DOWN', 'Break Even']
    
    # Count occurrences of each direction for each day
    day_of_week_dist = df_analysis.groupby('Day_Name')['Direction'].value_counts().unstack(fill_value=0)
    
    # Reindex to ensure consistent order of days and columns
    day_of_week_dist = day_of_week_dist.reindex(index=days_order, fill_value=0)
    day_of_week_dist = day_of_week_dist.reindex(columns=directions_order, fill_value=0)
    
    return day_of_week_dist
