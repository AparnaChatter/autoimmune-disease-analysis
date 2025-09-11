import os
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

from utils.io import RAW, write_csv
from utils.logging import get_logger

load_dotenv()
logger = get_logger("cdc")

# Example dataset (placeholder): set your CDC Socrata dataset ID here.
# Find dataset IDs at https://data.cdc.gov/ (e.g., arthritis indicators).
DATASET_ID = os.getenv("CDC_DATASET_ID", "")  # e.g., "9n3x-apgm" (example; verify on portal)
LIMIT = int(os.getenv("CDC_LIMIT", "50000"))

def fetch_cdc_dataset(dataset_id: str, limit: int = LIMIT) -> pd.DataFrame:
    if not dataset_id:
        raise ValueError("Set CDC_DATASET_ID in your environment or replace DATASET_ID here.")
    headers = {}
    token = os.getenv("CDC_APP_TOKEN")
    if token:
        headers["X-App-Token"] = token
    url = f"https://data.cdc.gov/resource/{dataset_id}.json?$limit={limit}"
    r = requests.get(url, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()
    return pd.DataFrame(data)

def main():
    df = fetch_cdc_dataset(DATASET_ID)
    # TODO: select/rename columns relevant to sex-stratified prevalence if available
    write_csv(df, RAW / f"cdc_{DATASET_ID or 'dataset'}.csv")
    logger.info(f"Wrote {len(df)} rows to data/raw/cdc_{DATASET_ID or 'dataset'}.csv")

if __name__ == "__main__":
    main()
