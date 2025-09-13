import pandas as pd
from src.utils.io import PROCESSED, write_csv
from src.utils.logging import get_logger

logger = get_logger("analyze")

def normalize(col: pd.Series) -> pd.Series:
    # Min-max within each disease to show trends comparably
    return (col - col.min()) / (col.max() - col.min() + 1e-9)

def main():
    p = PROCESSED / "merged_attention_signals.csv"
    if not p.exists():
        logger.warning("No merged_attention_signals.csv; run `make build` after fetching data.")
        return
    df = pd.read_csv(p)
    df["pubmed_norm"] = df.groupby("disease_id")["pubmed_count"].transform(normalize)
    df["trends_norm"] = df.groupby("disease_id")["interest"].transform(normalize)
    # attention gap proxy (positive means research > public attention)
    df["attention_gap"] = df["pubmed_norm"] - df["trends_norm"]
    write_csv(df, PROCESSED / "attention_scores.csv")
    logger.info(f"Analyzed {len(df)} rows into attention_scores.csv")

if __name__ == "__main__":
    main()
