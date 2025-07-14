
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