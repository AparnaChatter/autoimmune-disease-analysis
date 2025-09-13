import os, time, json, urllib.parse as up
from pathlib import Path
from datetime import datetime
import requests
import pandas as pd
import yaml
from dotenv import load_dotenv

from utils.io import RAW, write_csv
from utils.logging import get_logger

load_dotenv()
logger = get_logger("pubmed")

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
API_KEY = os.getenv("NCBI_API_KEY", "")

def build_query(term: str, y1: int, y2: int) -> str:
    date_range = f'("{y1}"[Date - Publication] : "{y2}"[Date - Publication])'
    return f"{term} AND {date_range}"

def yearly_counts(pubmed_query: str, y1: int, y2: int) -> pd.DataFrame:
    rows = []
    for year in range(y1, y2 + 1):
        params = {
            "db": "pubmed",
            "term": build_query(pubmed_query, year, year),
            "retmode": "json"
        }
        if API_KEY:
            params["api_key"] = API_KEY
        url = f"{BASE}?{up.urlencode(params)}"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        count = int(data["esearchresult"]["count"])
        rows.append({"year": year, "count": count})
        time.sleep(0.34 if API_KEY else 0.4)  # be polite
    return pd.DataFrame(rows)

def main():
    cfg = yaml.safe_load(Path("src/config/diseases.yaml").read_text())
    y1, y2 = cfg["years"]["start"], cfg["years"]["end"]
    out_frames = []
    for d in cfg["diseases"]:
        logger.info(f"Fetching PubMed counts for {d['name']}")
        df = yearly_counts(d["pubmed_query"], y1, y2)
        df["disease_id"] = d["id"]
        df["disease_name"] = d["name"]
        out_frames.append(df)
    out = pd.concat(out_frames, ignore_index=True)
    write_csv(out, RAW / "pubmed_counts_by_year.csv")
    logger.info(f"Wrote {len(out)} rows to data/raw/pubmed_counts_by_year.csv")

if __name__ == "__main__":
    main()
