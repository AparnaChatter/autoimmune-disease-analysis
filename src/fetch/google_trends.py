import os
import random
from pathlib import Path
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from pytrends.request import TrendReq
import yaml
from utils.io import RAW, write_csv
from utils.logging import get_logger
import time
from pytrends.exceptions import TooManyRequestsError
load_dotenv()
logger = get_logger("trends")

def main():
    cfg = yaml.safe_load(Path("src/config/diseases.yaml").read_text())
    y1, y2 = cfg["years"]["start"], cfg["years"]["end"]

    # Support rotating proxies from a comma-separated list in the environment variable
    proxy_list = os.getenv("GOOGLE_TRENDS_PROXIES")
    proxies = [p.strip() for p in proxy_list.split(",") if p.strip()] if proxy_list else []

    def get_pytrends():
        if proxies:
            proxy = random.choice(proxies)
            return TrendReq(hl="en-US", tz=0, proxies=[proxy])
        else:
            return TrendReq(hl="en-US", tz=0, proxies=[])

    frames = []
    for d in cfg["diseases"]:
        kw_list = d["trends_terms"]
        logger.info(f"Fetching trends for {d['name']}: {kw_list}")

        # Retry logic for both build_payload and interest_over_time, rotate proxy on each attempt
        for attempt in range(5):
            pytrends = get_pytrends()
            try:
                pytrends.build_payload(kw_list, timeframe=f"{y1}-01-01 {y2}-12-31", geo="")  # worldwide
                df = pytrends.interest_over_time()
                break
            except TooManyRequestsError:
                wait = 60 * (attempt + 1)
                logger.warning(f"429 error. Waiting {wait} seconds before retrying... Rotating proxy.")
                time.sleep(wait)
            except Exception as e:
                logger.warning(f"Error during pytrends request: {e}. Waiting {60 * (attempt + 1)} seconds before retrying... Rotating proxy.")
                time.sleep(60 * (attempt + 1))
        else:
            logger.error(f"Failed to fetch trends for {d['name']} after multiple attempts.")
            continue

        if df.empty:
            continue
        df = df.reset_index().rename(columns={"date": "date"})
        df["disease_id"] = d["id"]
        df["disease_name"] = d["name"]
        # Use the first keyword as primary signal (or average across terms)
        df["interest"] = df[kw_list].mean(axis=1)
        frames.append(df[["date", "interest", "disease_id", "disease_name"]])

        time.sleep(60)  # be polite

    out = pd.concat(frames, ignore_index=True)
    write_csv(out, RAW / "google_trends_interest.csv")
    logger.info(f"Wrote {len(out)} rows to data/raw/google_trends_interest.csv")

if __name__ == "__main__":
    main()
