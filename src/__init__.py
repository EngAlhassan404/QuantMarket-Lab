# FILE: src/__init__.py
# This file can be empty. It tells Python that the 'src' directory
# should be treated as a package, allowing for clean imports.

# =====================================================================================

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

# =====================================================================================

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

# =====================================================================================

# FILE: src/visualization.py
# -*- coding: utf-8 -*-
"""
This module handles the creation and saving of all plots for the analysis.
It generates a suite of professional, presentation-ready visualizations
to tell the story of the data.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os
import numpy as np

# Define a consistent, professional color palette for all plots
plt.style.use('seaborn-v0_8-whitegrid') 
PALETTE = {
    'UP': '#2ca02c',       # Forest Green
    'DOWN': '#d62728',     # Brick Red
    'Break Even': '#adb5bd' # Cool Grey
}

def generate_plots(df_analysis, day_of_week_dist, output_dir, asset_name, period_label):
    """Main function to generate and save all plots."""
    os.makedirs(output_dir, exist_ok=True)
    title_suffix = f"({asset_name} - {period_label})"
    filename_suffix = f"{asset_name}_{period_label.replace(' ', '_')}"
    paths = {}
    # Call each plotting function to generate a specific visualization
    paths['overall_dist_pie'] = plot_overall_distribution_pie(df_analysis, output_dir, title_suffix, filename_suffix)
    paths['cumulative_days'] = plot_cumulative_days_trend(df_analysis, output_dir, title_suffix, filename_suffix)
    paths['dow_dist_grouped'] = plot_day_of_week_distribution_grouped(day_of_week_dist, output_dir, title_suffix, filename_suffix)
    paths['cumulative_points'] = plot_cumulative_points_trend(df_analysis, output_dir, title_suffix, filename_suffix)
    return paths

def plot_overall_distribution_pie(df, output_dir, title_suffix, filename_suffix):
    """Creates and saves the overall direction distribution as a Pie Chart."""
    direction_counts = df['Direction'].value_counts().reindex(['UP', 'DOWN', 'Break Even']).fillna(0)
    fig, ax = plt.subplots(figsize=(10, 7), subplot_kw=dict(aspect="equal"))
    labels, sizes, colors = direction_counts.index, direction_counts.values, [PALETTE.get(l) for l in direction_counts.index]
    explode = (0.05, 0.05, 0)
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=None, autopct='%1.1f%%',
                                      startangle=90, colors=colors, pctdistance=0.85,
                                      wedgeprops=dict(width=0.4, edgecolor='w'))
    plt.setp(autotexts, size=10, weight="bold", color="white")
    ax.legend(wedges, [f'{l}: {s:,.0f} days' for l, s in zip(labels, sizes)],
              title="Direction", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=12)
    ax.set_title(f'Overall Distribution of Daily Directions\n{title_suffix}', fontsize=16, weight='bold')
    filepath = output_dir / f"{filename_suffix}_OverallDistribution_Pie.png"
    plt.tight_layout()
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath

def plot_day_of_week_distribution_grouped(dist_df, output_dir, title_suffix, filename_suffix):
    """Creates and saves the day-of-the-week distribution as a Grouped Bar Chart."""
    fig, ax = plt.subplots(figsize=(14, 8))
    dist_df.plot(kind='bar', stacked=False, color=[PALETTE.get(c) for c in dist_df.columns], ax=ax, width=0.8)
    ax.set_title(f'Daily Direction Count by Day of the Week\n{title_suffix}', fontsize=16, weight='bold')
    ax.set_xlabel('Day of the Week', fontsize=12)
    ax.set_ylabel('Number of Days', fontsize=12)
    ax.legend(title='Direction', fontsize=11)
    ax.tick_params(axis='x', rotation=0, labelsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for container in ax.containers:
        ax.bar_label(container, label_type='edge', fontsize=9, padding=3)
    filepath = output_dir / f"{filename_suffix}_DayOfWeekDistribution_Grouped.png"
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    return filepath

def plot_cumulative_points_trend(df, output_dir, title_suffix, filename_suffix):
    """Creates and saves the cumulative trend of UP vs DOWN points over time."""
    df_plot = df.copy()
    df_plot['UP_Points'] = df_plot.where(df_plot['Direction'] == 'UP')['Points_Display'].fillna(0)
    df_plot['DOWN_Points'] = df_plot.where(df_plot['Direction'] == 'DOWN')['Points_Display'].abs().fillna(0)
    df_plot['CUM_UP_Points'] = df_plot['UP_Points'].cumsum()
    df_plot['CUM_DOWN_Points'] = df_plot['DOWN_Points'].cumsum()
    plt.figure(figsize=(15, 8))
    plt.plot(df_plot['Date'], df_plot['CUM_UP_Points'], label='Cumulative UP Points', color=PALETTE['UP'], linewidth=2.5)
    plt.plot(df_plot['Date'], df_plot['CUM_DOWN_Points'], label='Cumulative DOWN Points (Magnitude)', color=PALETTE['DOWN'], linewidth=2.5)
    plt.title(f'Cumulative Points Trend (UP vs. DOWN Days)\n{title_suffix}', fontsize=16, weight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative Points (Scaled)', fontsize=12)
    plt.legend(loc='upper left', fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    filepath = output_dir / f"{filename_suffix}_CumulativePoints_Trend.png"
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    return filepath

def plot_cumulative_days_trend(df, output_dir, title_suffix, filename_suffix):
    """Creates and saves the cumulative trend of days."""
    df_plot = df.copy()
    df_plot['UP_Cumulative'] = (df_plot['Direction'] == 'UP').cumsum()
    df_plot['DOWN_Cumulative'] = (df_plot['Direction'] == 'DOWN').cumsum()
    df_plot['BreakEven_Cumulative'] = (df_plot['Direction'] == 'Break Even').cumsum()
    plt.figure(figsize=(15, 8))
    plt.stackplot(df_plot['Date'], df_plot['UP_Cumulative'], df_plot['DOWN_Cumulative'], df_plot['BreakEven_Cumulative'], 
                  labels=['UP Days', 'DOWN Days', 'Break Even Days'],
                  colors=[PALETTE['UP'], PALETTE['DOWN'], PALETTE['Break Even']], alpha=0.8)
    plt.title(f'Cumulative Count of Daily Directions Over Time\n{title_suffix}', fontsize=16, weight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative Number of Days', fontsize=12)
    plt.legend(loc='upper left', fontsize=12)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    filepath = output_dir / f"{filename_suffix}_CumulativeDays_Trend.png"
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    return filepath

# =====================================================================================

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

# =====================================================================================

# FILE: src/utils.py
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
    # This assumes utils.py is in src/, so we need to go up two levels.
    return Path(__file__).parent.parent

def get_period_label(start_date, end_date):
    """Creates a standardized, file-safe text label for a time period."""
    start_str = start_date.strftime('%Y%m%d') if pd.notna(start_date) else 'Start'
    end_str = end_date.strftime('%Y%m%d') if pd.notna(end_date) else 'End'
    return f"{start_str}_to_{end_str}"

def filter_data_by_date(df, start_date, end_date):
    """Filters a DataFrame based on a start and end date."""
    if df is None or df.empty:
        return pd.DataFrame()
    # Default to the full range if dates are not provided
    start = start_date if start_date else df['Date'].min()
    end = end_date if end_date else df['Date'].max()
    mask = (df['Date'] >= start) & (df['Date'] <= end)
    return df.loc[mask].copy()

def setup_output_directory(root_results_dir, asset_name, period_label):
    """Creates and returns the path for an analysis run's output directory."""
    path = root_results_dir / asset_name / period_label
    os.makedirs(path, exist_ok=True)
    return path
