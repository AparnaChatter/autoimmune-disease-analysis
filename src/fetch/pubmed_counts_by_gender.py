# Script to fetch PubMed publication counts by gendered queries for autoimmune diseases
import os
import time
import yaml
import pandas as pd
from utils.io import RAW, write_csv
from utils.logging import get_logger

logger = get_logger("pubmed_gender")

def build_gender_query(base_query, gender):
    return f"({base_query}) AND {gender}"

import requests
import urllib.parse as up
from dotenv import load_dotenv
load_dotenv()
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
        time.sleep(0.34 if API_KEY else 0.4)
    return pd.DataFrame(rows)

def main():
    cfg = yaml.safe_load(open("src/config/diseases.yaml", "r", encoding="utf-8").read())
    y1, y2 = cfg["years"]["start"], cfg["years"]["end"]
    genders = ["women", "men"]
    out_frames = []
    for d in cfg["diseases"]:
        for gender in genders:
            query = build_gender_query(d["pubmed_query"], gender)
            logger.info(f"Fetching PubMed counts for {d['name']} + {gender}")
            df = yearly_counts(query, y1, y2)
            df["disease_id"] = d["id"]
            df["disease_name"] = d["name"]
            df["gender"] = gender
            out_frames.append(df)
    out = pd.concat(out_frames, ignore_index=True)
    write_csv(out, RAW / "pubmed_counts_by_gender.csv")
    logger.info(f"Wrote {len(out)} rows to data/raw/pubmed_counts_by_gender.csv")

if __name__ == "__main__":
    main()
