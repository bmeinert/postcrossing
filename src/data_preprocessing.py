"""
Postcrossing Data Pipeling: Cleaning and Preprocessing
===============================================================

Author: /bmeinert
Date: 2026-01-18
Version: 1.0.0
Description: Extracts Postcrossing export data (JSON), performs data 
             cleansing, and calculates logistics KPIs (travel days/1000km).
             Processes data for global postal transit time analysis.
             Contains excerpt of sent and received postcards only.

License: 
        Code: MIT License
        Data and Visualizations: CC BY-SA 4.0

"""


import pandas as pd
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def process_single_file(file_path):
    """Processes single JSON-file and returns cleaned Dataframe."""
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
        if "received" in file_path.name.lower() and len(parts) >= 3:
            df["country_id_dest"] = parts[1].upper()
        
        if len(parts) >= 4:
            df["extraction_date"] = pd.to_datetime(parts[3], format="%Y%m%d", errors='coerce')
            invalid_dates = df["extraction_date"].isna().sum()
            if invalid_dates >  0:
                logging.warning(f"{invalid_dates} invalid extraction dates in {file_path.name}.")

        # Transformations
        df["sent_date"] = pd.to_datetime(df["sent_date"], unit="s").dt.normalize()
        df["received_date"] = pd.to_datetime(df["received_date"], unit="s").dt.normalize()
        df["country_id_origin"] = df["postcard_id"].str.split("-", expand=True)[0]
        
        # efficiency metric: days per 1000km
        df["days_per_1000km"] = (df["travel_time_days"] / (df["distance_km"] / 1000)).round(2)
        df["travel_route"] = df["country_id_origin"] + "-" + df["country_id_dest"]
        
        # clean columns
        drop_cols = ["unknown", "user", "image_exists"]
        df = df.drop(columns=[c for c in drop_cols if c in df.columns])
        
        return df

    except (json.JSONDecodeError, KeyError) as e:
        logging.error(f"Error while parsing {file_path.name}: {e}")
        return None

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
    logging.info(f"Processed {num_files} files with total {len(df_all)} unique postcards.") 
    return df_all

if __name__ == "__main__":
    # path configuration
    BASE_DIR = Path(__file__).resolve().parent
    #RAW_DATA_DIR = "D:/Datenprojekte/Postcrossing/data/raw"
    RAW_DATA_DIR = BASE_DIR.parent / "data" / "raw"
    #OUTPUT_FILE = "D:/Datenprojekte/Postcrossing/data/processed/cleaned_data.csv"
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
    else:
        logging.error("No data extracted.")