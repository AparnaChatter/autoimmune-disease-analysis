from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from src.utils.io import PROCESSED, REPORTS
from src.utils.logging import get_logger

logger = get_logger("viz")

def lineplot(df: pd.DataFrame, y: str, title: str, outfile: Path):
    plt.figure()
    for name, grp in df.groupby("disease_name"):
        grp = grp.sort_values("year")
        plt.plot(grp["year"], grp[y], label=name)
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel(y)
    plt.legend()
    outfile.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()

def main():
    p = PROCESSED / "attention_scores.csv"
    if not p.exists():
        logger.warning("attention_scores.csv not found. Run `make build`.")
        return
    df = pd.read_csv(p)

    lineplot(df, "pubmed_count", "PubMed article counts by disease", REPORTS / "pubmed_counts.png")
    lineplot(df, "interest", "Google Trends interest by disease", REPORTS / "trends_interest.png")
    lineplot(df, "attention_gap", "Attention gap (research - public) by disease", REPORTS / "attention_gap.png")
    logger.info("Saved plots to reports/")

if __name__ == "__main__":
    main()
