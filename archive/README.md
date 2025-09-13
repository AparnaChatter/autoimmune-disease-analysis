This directory contains archived helper and legacy scripts that are not required for the current KWK gendered analysis workflow.

These files were moved into `archive/` to keep the repository focused on the active scripts used to reproduce the KWK submission. They remain in version control history and show how the project required iterating through multiple different methods and sources before consolidation.

Files archived here and why:

- `clean_merge.py` — legacy, non-gendered transform pipeline. Functionality now provided by `src/transform/clean_merge_gendered.py`.
- `merge_gender_data.py` — placeholder stub (no implementation).
- `pubmed_counts.py` — legacy non-gendered PubMed fetcher; replaced by `pubmed_counts_by_gender.py` for gendered counts.
- `google_trends_selenium.py` — brittle Selenium helper used for manual downloads; not required by the automated `pytrends` fetcher.
- `google_trends_by_gender.py` — small helper that prints gendered terms (kept here for reference).
- `plots.py` — legacy plotting helper that expects older artifact names; replaced by `src/visualization/*` scripts.
- `ratios_time_series.py` — legacy analysis script that writes `attention_scores.csv`; functionality consolidated elsewhere.
