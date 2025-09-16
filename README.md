# Autoimmune Disease Gender Disparities

Author: Aparna Chatterjee

## Project focus

1.  How does the female:male burden/prevalence ratio vary across selected autoimmune diseases?
2.  How does public and research attention (Google Trends, PubMed counts) trend relative to estimated burden (CDC mortality/prevalence where available)?
3.  Which disease x gender pairs show the strongest (positive or negative) associations between interest, publications, and burden?

## Datasets & provenance

- PubMed (NCBI E-utilities) - yearly article counts by disease (proxy for research attention). See `src/fetch/pubmed_counts_by_gender.py`.
- Google Trends - monthly search interest (gendered where available). Raw CSVs are stored in `data/raw/`.
- CDC WONDER / Compressed Mortality File (downloaded CSVs) - sex-stratified counts where available (raw CDC files in `data/raw/` and processed results in `data/processed/`).

## How to reproduce the analysis

1. Clone and open the repo

```bash
git clone https://github.com/AparnaChatter/autoimmune-disease-analysis.git
cd autoimmune-disease-analysis
```

2. Create the environment and install dependencies (or use an existing Python 3.10+ environment)

```bash
conda create -n autoimmune-disease python=3.11 -y
conda activate autoimmune-disease
pip install -r requirements.txt
```

3. Fetch or place raw data in `data/raw/` (all CDC and Google Trends CSVs were downloaded manually for this project due to the API not working and web scraping being blocked on Google Trends). To run the included fetchers:

Note: If you encounter issues where PYTHONPATH is not recognized, remove the `PYTHONPATH=src` prefix and run the scripts directly with `python src/...`.

```bash
# fetch yearly PubMed counts classified by gender
PYTHONPATH=src python src/fetch/pubmed_counts_by_gender.py
# fetch Google Trends interest for configured terms
PYTHONPATH=src python src/fetch/google_trends.py
# fetch CDC WONDER data (if API access is available)
PYTHONPATH=src python src/fetch/cdc_wonder_by_gender.py
```

4. Clean and merge the signals

Main cleaning and merge pipeline that produces `data/processed/merged_gendered_signals.csv`

```bash
PYTHONPATH=src python src/transform/clean_merge_gendered.py
```

5. Run analyses & visualizations

```bash
# compute lagged correlations and save heatmaps
PYTHONPATH=src python src/visualization/plot_correlations.py
# follow-up analyses (z-overlays, CCF plots, Granger wrappers)
PYTHONPATH=src python src/visualization/corr_followups.py
# additional time-series and correlation plots by gender
PYTHONPATH=src python src/visualization/gender_disparity_plots.py
```

Outputs (figures and CSVs) are written to the `reports/` directory. The primary merged dataset is at `data/processed/merged_gendered_signals.csv` and the correlation summary is at `reports/correlation_summary.csv`.

## Interpretation & limitations

- PubMed counts are a proxy for research attention, they do not represent sample sizes or study focus exclusively on one sex.
- Google Trends reflects search interest in the population using Google and should be interpreted with geographic and demographic caveats.
- CDC tables are authoritative but are not uniformly available for all diseases - missing values are handled conservatively in the processing scripts.

## Credits

- Author: Aparna Chatterjee
- AI Assistance (GitHub CoPilot):
  - Helped diagnose environment and package issues.
  - The AI assistant provided some code snippets and debugging help.

## Citations

Centers for Disease Control and Prevention, National Center for Health Statistics. National Vital Statistics System, Mortality: Compressed Mortality File. Accessed Sep 13, 2025.
