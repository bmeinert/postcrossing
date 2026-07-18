"""
Postcrossing Data Pipeling: Cleaning and Preprocessing
===============================================================

Author: /bmeinert
Date: 2026-03-03
Version: 1.1.0
Description: Extracts Postcrossing export data (JSON), performs data 
             cleansing, and calculates logistics KPIs (travel days/1000km).
             Processes data for global postal transit time analysis.
             Contains excerpt of sent and received postcards only.

License: 
        Code: MIT License
        Data and Visualizations: CC BY-SA 4.0

"""

import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
import hashlib
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def process_single_file(file_path):
    """Processes single JSON-file and returns cleaned Dataframe."""

    SALT = os.getenv("SALT", "default_salt_value")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        column_names = [
            "postcard_id", "user", "unknown", "country_id_dest",
            "sent_date", "received_date", "distance_km",
            "travel_time_days", "image_exists"
        ]
        
        df = pd.DataFrame(data, columns=column_names)
        
        # Extraction from filename
        parts = file_path.stem.split("_")
        num_parts = len(parts)
        if num_parts < 4:
             logging.warning(f"Filename {file_path.name} has only {num_parts} parts."
                             "Expected format: type_country_user_date.json")
        
        file_type = parts[0].lower() if len(parts) >= 1 else "unknown" 
        user_country_from_filename = parts[1].upper() if num_parts >= 2 else "unknown"
        user_from_filename = parts[2].lower() if num_parts>= 3 else"unknown"
        
        # File type
        if file_type == "unknown":
            logging.error(f"Could not determine file type for {file_path.name}.")
        df["type"] = file_type
        
        # User(sender) logic
        if "received" in file_type:
            df["country_id_dest"]= user_country_from_filename
            df["user_origin_raw"] = df["user"]
        elif "sent" in file_type:
            df["user_origin_raw"] = user_from_filename
        else:
            df["user_origin_raw"] = "unknown"

        # User country
        df["user_country"] = user_country_from_filename

        # Extraction date
        if num_parts >= 4:
            df["extraction_date"] = pd.to_datetime(parts[3], format="%Y%m%d", errors='coerce')                
            if df["extraction_date"].isna().all():
                logging.warning(f"Date format error in '{file_path.name}': '{parts[3]}' is not YYYYMMDD.")
        else:
            df["extraction_date"] = pd.NaT
            logging.warning(f"Missing date part in filename: '{file_path.name}'. Expected at least 4 parts.")

        # Anonymization
        unique_user = str(df["user_origin_raw"].iloc[0]) if not df.empty else "none"
        user_hash = hashlib.sha256(f"{unique_user}{SALT}".encode()).hexdigest()[:8]
        df["user_name_origin"] = user_hash

        # Date transformation
        df["sent_date"] = pd.to_datetime(df["sent_date"], unit="s").dt.normalize()
        df["received_date"] = pd.to_datetime(df["received_date"], unit="s").dt.normalize()

        # Country ID Origin extraction from postcard_id
        df["country_id_origin"] = df["postcard_id"].str.split("-", expand=False).str[0]

        # Metrics and additional columns
        df["days_per_1000km"] = (df["travel_time_days"] / (df["distance_km"].replace(0, np.nan) / 1000)).round(2)
        df["travel_route"] = df["country_id_origin"].astype(str) + "-" + df["country_id_dest"].astype(str)

        # Cleanup
        drop_cols = ["unknown", "user", "image_exists", "user_origin_raw"]
        return df.drop(columns=[c for c in drop_cols if c in df.columns])
    
    except Exception as e:
        logging.error(f"Error while parsing {file_path.name}: {e}")
        return pd.DataFrame()
    

def load_all_data(folder_path):
    """Scans folder and concatenates all dataframes."""
    path = Path(folder_path)
    file_paths = list(path.glob("*.json"))
    
    if not file_paths:
        logging.warning(f"No JSON files found in {folder_path}.")
        return pd.DataFrame()

    df_list = []
    for file in file_paths:
        df_temp = process_single_file(file)
        if df_temp is not None:
            df_list.append(df_temp)

    if not df_list:
        logging.error("No valid data extracted from files.")
        return pd.DataFrame()

    # Final concatenation and deduplication
    num_files = len(file_paths)
    df_all = pd.concat(df_list, ignore_index=True)

    df_all = df_all.drop_duplicates(subset=["postcard_id"])
    df_all = df_all.drop(columns=["postcard_id"]) # delete ID after deduplication

    # Fixing Namibia country code
    if "country_id_dest" in df_all.columns:
        df_all["country_id_dest"] = df_all["country_id_dest"].astype(str)
        df_all["country_id_dest"] = df_all["country_id_dest"].replace(['nan', 'None', 'NaN'], 'NA').astype(str)
    if "country_id_origin" in df_all.columns:
        df_all["country_id_origin"] = df_all["country_id_origin"].astype(str)
        df_all["country_id_origin"] = df_all["country_id_origin"].replace(['nan', 'None', 'NaN'], 'NA').astype(str)

    logging.info(f"Processed {num_files} files with total {len(df_all)} unique postcards.") 

    return df_all

if __name__ == "__main__":
    # path configuration
    BASE_DIR = Path(__file__).resolve().parent
    RAW_DATA_DIR = BASE_DIR.parent / "data" / "raw"
    OUTPUT_FILE = BASE_DIR.parent / "data" / "processed" / "cleaned_data.csv"

    logging.info("Starts data processing...")
    df_final = load_all_data(RAW_DATA_DIR)

    if not df_final.empty:
        logging.info(f"{len(df_final)} datasets processed successfully.")
        logging.info(f"Columns: {list(df_final.columns)}")
        
        # Saving final dataframe
        df_final.to_csv(OUTPUT_FILE, index=False, date_format='%Y-%m-%d', encoding='utf-8')
        logging.info(f"Cleaned data saved to {OUTPUT_FILE}.")
        print(df_final.head())
        print("Missing values: ", df_final.isna().sum()) 
        print(df_final['type'].value_counts())
    else:
        logging.error("No data extracted.")