# -*- coding: utf-8 -*-
"""
=====================================================================================
# QuantMarket-Lab - Step 1: Data Acquisition Pipeline
#
# Fetches latest daily financial data from Alpha Vantage API and saves it to
# the `data/raw` directory.
=====================================================================================
"""
import pandas as pd
import requests
import yaml
import time
import shutil
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

def manage_backups(source_file_path, asset_name, config):
    """Creates timestamped backups of raw data files before modification."""
    if not config['backup_settings']['enable_backups']:
        return
    try:
        backup_root_folder = get_project_root() / '_Backups'
        backup_dir = backup_root_folder / asset_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        if not source_file_path.exists():
            return

        existing_backups = sorted(backup_dir.glob(f"{asset_name}_backup_*.csv"), key=os.path.getmtime)
        while len(existing_backups) >= config['backup_settings']['max_backups_per_asset']:
            oldest_backup = existing_backups.pop(0)
            oldest_backup.unlink()
            print(f"    -> 🗑️ Deleted oldest backup: {oldest_backup.name}")

        today_str = pd.Timestamp.now().strftime('%Y-%m-%d')
        backup_file_path = backup_dir / f"{asset_name}_backup_{today_str}.csv"
        if not backup_file_path.exists():
            shutil.copy2(source_file_path, backup_file_path)
            print(f"    -> 🛡️ Successfully created backup: {backup_file_path.name}")
    except Exception as e:
        print(f"    -> ❌ Error during backup process: {e}")

def fetch_and_update_asset(asset_config, api_key, raw_data_root):
    """Fetches and updates data for a single asset into the raw directory."""
    asset_name = asset_config["user_name"]
    print(f"\n--- 🔄 Processing: {asset_name} ---")
    summary = {"asset": asset_name, "status": "❌ Failed", "latest_date": None, "details": ""}
    local_file_path = raw_data_root / asset_name / f"{asset_name}.csv"

    manage_backups(local_file_path, asset_name, load_config())

    try:
        df_existing = pd.read_csv(local_file_path, parse_dates=['Date']) if local_file_path.exists() else pd.DataFrame()
        print(f"    -> 📂 Found local raw file with {len(df_existing)} records." if not df_existing.empty else "    -> 📄 No local raw file found, creating new file.")

        # --- THIS IS THE CORRECTED SECTION ---
        # Construct the appropriate API URL based on asset type without extra spaces.
        if asset_config["type"] == "FX":
            url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={asset_config["av_from"]}&to_symbol={asset_config["av_to"]}&outputsize=full&apikey={api_key}'
            data_key = 'Time Series FX (Daily)'
        elif asset_config["type"] == "COMMODITY":
             url = f'https://www.alphavantage.co/query?function={asset_config["av_function"]}&interval=daily&apikey={api_key}'
             data_key = 'data'
        else:
            summary['details'] = f"Unsupported asset type: {asset_config['type']}"
            print(f"    -> ❌ {summary['details']}")
            return summary
        # --- END OF CORRECTION ---

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data_key not in data:
            error_msg = data.get('Note') or data.get('Information') or data.get('Error Message', 'Unknown API error')
            summary["details"] = error_msg
            print(f"    -> ❌ API Error for {asset_name}: {error_msg}")
            return summary

        df_new = pd.DataFrame.from_dict(data[data_key], orient='index')
        df_new.index = pd.to_datetime(df_new.index)
        
        if asset_config["type"] == "COMMODITY":
            df_new = df_new.rename(columns={'value': 'Close'})
            df_new['Open'] = df_new['Close'].shift(1)
            df_new['High'] = df_new[['Open', 'Close']].max(axis=1)
            df_new['Low'] = df_new[['Open', 'Close']].min(axis=1)
            df_new.dropna(inplace=True)
        else: # Forex
            df_new.rename(columns=lambda x: x.split('. ')[1].capitalize(), inplace=True)

        df_new = df_new[['Open', 'High', 'Low', 'Close']].astype(float)
        df_new.reset_index(inplace=True)
        df_new.rename(columns={'index': 'Date'}, inplace=True)

        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(subset=['Date'], keep='last', inplace=True)
        df_combined.sort_values(by='Date', inplace=True, ignore_index=True)
        
        os.makedirs(local_file_path.parent, exist_ok=True)
        df_combined.to_csv(local_file_path, index=False)
        
        newly_added_count = len(df_combined) - len(df_existing)
        print(f"    -> ✅ Added {newly_added_count} new records to raw data. Total records: {len(df_combined)}.")
        
        summary["status"] = "✅ Succeeded"
        summary["latest_date"] = df_combined['Date'].max()
        return summary
    except Exception as e:
        summary["details"] = str(e)
        print(f"    -> ❌ Unexpected error while processing {asset_name}: {e}")
        return summary

if __name__ == "__main__":
    config = load_config()
    PROJECT_ROOT = get_project_root()
    RAW_DATA_ROOT = PROJECT_ROOT / 'data' / 'raw'
    
    print(f"🚀 Starting Data Acquisition Pipeline 🚀")
    print(f"   (Saving data to: {RAW_DATA_ROOT})")
    
    run_results = []
    assets_to_process = config['assets']
    for i, asset in enumerate(assets_to_process):
        result = fetch_and_update_asset(asset, config['api_settings']['alpha_vantage_key'], RAW_DATA_ROOT)
        run_results.append(result)
        if i < len(assets_to_process) - 1:
            delay = config['api_settings']['api_call_delay_seconds']
            print(f"    -> ⏳ Waiting for {delay} seconds...")
            time.sleep(delay)
    
    print("\n\n🎉 Data acquisition complete! 🎉")
