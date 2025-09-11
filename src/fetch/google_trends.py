import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from pytrends.request import TrendReq
import yaml
from utils.io import RAW, write_csv
from utils.logging import get_logger
import time
load_dotenv()
logger = get_logger("trends")

def main():
    cfg = yaml.safe_load(Path("src/config/diseases.yaml").read_text())
    y1, y2 = cfg["years"]["start"], cfg["years"]["end"]

    proxy = os.getenv("GOOGLE_TRENDS_PROXY")
    pytrends = TrendReq(hl="en-US", tz=0, proxies=[proxy] if proxy else [])

    frames = []
    for d in cfg["diseases"]:
        kw_list = d["trends_terms"]
        logger.info(f"Fetching trends for {d['name']}: {kw_list}")
        pytrends.build_payload(kw_list, timeframe=f"{y1}-01-01 {y2}-12-31", geo="")  # worldwide
        df = pytrends.interest_over_time()
        if df.empty:
            continue
        df = df.reset_index().rename(columns={"date": "date"})
        df["disease_id"] = d["id"]
        df["disease_name"] = d["name"]
        # Use the first keyword as primary signal (or average across terms)
        df["interest"] = df[kw_list].mean(axis=1)
        frames.append(df[["date", "interest", "disease_id", "disease_name"]])

        time.sleep(20)  # be polite

    out = pd.concat(frames, ignore_index=True)
    write_csv(out, RAW / "google_trends_interest.csv")
    logger.info(f"Wrote {len(out)} rows to data/raw/google_trends_interest.csv")

if __name__ == "__main__":
    main()
