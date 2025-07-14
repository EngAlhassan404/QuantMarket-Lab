
# FILE: src/reporting.py
# -*- coding: utf-8 -*-
"""
This module is responsible for generating and saving all file-based outputs
of the analysis, including the detailed text summary report and a CSV file
of the processed data with all added features.
"""
import os
import pandas as pd
import numpy as np

def save_summary_report(summary_stats, day_of_week_dist, output_dir, asset_name, period_label):
    """Saves the text summary report of the analysis."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{asset_name}_{period_label.replace(' ', '_')}_SummaryReport.txt"
    filepath = output_dir / filename
    point_decimals = summary_stats.get('point_decimals', 2)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"{asset_name} Daily Direction Analysis Report\n")
        f.write(f"Analysis Period Label: {period_label}\n")
        f.write(f"Actual Analyzed Period: {summary_stats['actual_start_date']} to {summary_stats['actual_end_date']}\n")
        f.write(f"Report Generation Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        f.write("I. Overall Daily Direction Statistics:\n")
        f.write(f"  Total Trading Days Analyzed: {summary_stats['total_days']}\n")
        f.write(f"  UP Days: {summary_stats['up_days']} ({summary_stats['up_pct']:.2f}%)\n")
        f.write(f"  DOWN Days: {summary_stats['down_days']} ({summary_stats['down_pct']:.2f}%)\n")
        f.write(f"  Break Even Days: {summary_stats['break_even_days']} ({summary_stats['break_even_pct']:.2f}%)\n\n")
        
        f.write(f"II. Points Summary (Scaled by {summary_stats['point_multiplier']}):\n")
        f.write(f"  Total Scaled Points on UP Days: {summary_stats['total_up_points_display']:.{point_decimals}f}\n")
        f.write(f"  Total Scaled Points on DOWN Days (sum of magnitudes): {summary_stats['total_down_points_display']:.{point_decimals}f}\n")
        f.write(f"  Net Scaled Points (UP Points - DOWN Points): {summary_stats['net_points_display']:.{point_decimals}f}\n\n")

        f.write("III. Longest Consecutive Streaks:\n")
        f.write(f"  Longest UP Streak: {summary_stats['longest_up_streak']} days\n")
        f.write(f"  Longest DOWN Streak: {summary_stats['longest_down_streak']} days\n")
        f.write(f"  Longest Break Even Streak: {summary_stats['longest_break_even_streak']} days\n\n")

        f.write("IV. Daily Direction Distribution by Day of the Week:\n")
        dist_with_pct = day_of_week_dist.copy()
        dist_with_pct['Total'] = dist_with_pct.sum(axis=1)
        for col in ['UP', 'DOWN', 'Break Even']:
            if col in dist_with_pct.columns and dist_with_pct['Total'].sum() > 0:
                 dist_with_pct[f'{col}_%'] = (dist_with_pct[col] / dist_with_pct['Total'].replace(0, np.nan)).mul(100).fillna(0).round(2)
        
        f.write(dist_with_pct.to_string())
        f.write("\n\n" + "="*80 + "\nEnd of Report\n")
    return filepath

def save_processed_data_to_csv(df_analysis, output_dir, asset_name, period_label):
    """Saves the processed data with all added features to a CSV file."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{asset_name}_{period_label.replace(' ', '_')}_DailyDirectionData.csv"
    filepath = output_dir / filename
    cols_to_save = ['Date', 'Open', 'High', 'Low', 'Close', 'Day_Name', 'Direction', 'Raw_Points', 'Points_Display']
    existing_cols = [col for col in cols_to_save if col in df_analysis.columns]
    df_analysis[existing_cols].to_csv(filepath, index=False, encoding='utf-8', float_format='%.4f')
    return filepath