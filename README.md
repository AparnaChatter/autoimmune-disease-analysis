# Autoimmune Gender Disparities — KWK Applied Data Science Fundamentals Challenge (Summer 2025)

Author: Aparna Chatterjee

This repository is Aparna Chatterjee's project submission for the KWK Applied Data Science Fundamentals Challenge (Summer 2025). The analysis quantifies and visualizes gendered differences in autoimmune disease indicators using public sources (PubMed, Google Trends, and CDC-derived data), and demonstrates reproducible data collection, cleaning, exploratory analysis and data visualization.

## Project focus

- Research questions
  1.  How does the female:male burden/prevalence ratio vary across selected autoimmune diseases?
  2.  How does public and research attention (Google Trends, PubMed counts) trend relative to estimated burden (CDC mortality/prevalence where available)?
  3.  Which disease × gender pairs show the strongest (positive or negative) associations between interest, publications, and burden?

## Datasets & provenance

- PubMed (NCBI E-utilities) — yearly article counts by disease (proxy for research attention). See `src/fetch/pubmed_counts_by_gender.py`.
- Google Trends — monthly search interest (gendered where available). Raw CSVs are stored in `data/raw/`.
- CDC WONDER / Compressed Mortality File (downloaded CSVs) — sex-stratified counts where available (raw CDC files in `data/raw/` and processed results in `data/processed/`).

Full citation used in analysis (mortality data):

Centers for Disease Control and Prevention, National Center for Health Statistics. National Vital Statistics System, Mortality: Compressed Mortality File. Accessed Sep 13, 2025.

## How to reproduce the analysis (condensed)

Recommended: use the provided conda environment (the project was developed using a conda env named `autoimmune-disease`). Example commands below assume you have conda installed.

1. Clone and open the repo

```bash
git clone https://github.com/<you>/autoimmune-gender-disparities.git
cd autoimmune-gender-disparities
```

2. Create the environment and install deps (or use an existing Python 3.10+ environment)

```bash
conda create -n autoimmune-disease python=3.11 -y
conda activate autoimmune-disease
pip install -r requirements.txt
```

3. Fetch or place raw data in `data/raw/` (all CDC CSVs were downloaded manually for this project). To run the included fetchers:

```bash
# run from repo root so imports work as intended
PYTHONPATH=src python src/fetch/pubmed_counts_by_gender.py
PYTHONPATH=src python src/fetch/fetch_trends_example.py  # if available
```

4. Clean and merge the signals

```bash
PYTHONPATH=src python src/transform/clean_merge_gendered.py
```

5. Run analyses & visualizations

```bash
PYTHONPATH=src python src/visualization/plot_correlations.py
PYTHONPATH=src python src/visualization/corr_followups.py
PYTHONPATH=src python src/visualization/gender_disparity_plots.py
```

Outputs (figures and CSVs) are written to the `reports/` directory. The primary merged dataset is `data/processed/merged_gendered_signals.csv` and the correlation summary is `reports/correlation_summary.csv`.

## Interpretation & limitations

- PubMed counts are a proxy for research attention (mention counts) — they do not represent sample sizes or study focus exclusively on one sex.
- Google Trends reflects search interest in the population using Google and should be interpreted with geographic and demographic caveats.
- CDC tables are authoritative but are not uniformly available for all diseases — missing values are handled conservatively in the processing scripts.

## Credits

- Author: Aparna Chatterjee (primary author; project owner)
- AI Assistance(GitHub CoPilot):

  - Helped diagnose environment and package issues and installed required packages into the project conda environment (`numpy`, `pandas`, `matplotlib`, `seaborn`, `scipy`, `statsmodels`) so plotting and statistical tests could run.

  - The AI assistant provided code, debugging, and automation support.
