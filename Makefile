PY=python

fetch_pubmed:
	$(PY) src/fetch/pubmed_counts.py

fetch_trends:
	$(PY) src/fetch/google_trends.py

fetch_cdc_example:
	$(PY) src/fetch/cdc_socrata_generic.py

transform:
	$(PY) src/transform/clean_merge.py

analyze:
	$(PY) src/analyze/ratios_time_series.py

viz:
	$(PY) src/viz/plots.py

build: fetch_pubmed fetch_trends transform analyze viz
