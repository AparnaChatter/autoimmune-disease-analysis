from pathlib import Path
import pandas as pd
from src.utils.io import RAW, PROCESSED, write_csv
from src.utils.logging import get_logger

logger = get_logger("transform")

def load_pubmed() -> pd.DataFrame:
    p = RAW / "pubmed_counts_by_year.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

def load_trends() -> pd.DataFrame:
    p = RAW / "google_trends_interest.csv"
    return pd.read_csv(p, parse_dates=["date"]) if p.exists() else pd.DataFrame()

def load_cdc_any() -> pd.DataFrame:
    # grab the first CDC file if present
    cdc_files = list((RAW).glob("cdc_*.csv"))
    return pd.read_csv(cdc_files[0]) if cdc_files else pd.DataFrame()

def main():
    pubmed = load_pubmed()
    trends = load_trends()
    cdc = load_cdc_any()

    # pubmed tidy
    if not pubmed.empty:
        pubmed_tidy = pubmed.rename(columns={"count":"pubmed_count","year":"year"})[
            ["year","pubmed_count","disease_id","disease_name"]
        ]
        write_csv(pubmed_tidy, PROCESSED / "pubmed_tidy.csv")

    # trends yearly mean
    if not trends.empty:
        trends["year"] = trends["date"].dt.year
        trends_yearly = (trends
                         .groupby(["year","disease_id","disease_name"], as_index=False)
                         .agg(interest=("interest","mean")))
        write_csv(trends_yearly, PROCESSED / "trends_yearly.csv")

    # optional CDC harmonization stub (depends on chosen dataset schema)
    if not cdc.empty:
        cdc.to_csv(PROCESSED / "cdc_raw_passthrough.csv", index=False)

    # merge pubmed + trends (inner on year/disease)
    if not pubmed.empty and not trends.empty:
        merged = (pubmed_tidy
                  .merge(trends_yearly, on=["year","disease_id","disease_name"], how="inner"))
        write_csv(merged, PROCESSED / "merged_attention_signals.csv")
        logger.info(f"Merged attention rows: {len(merged)}")

if __name__ == "__main__":
    main()
