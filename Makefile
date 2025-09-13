PY=python

fetch_pubmed:
	$(PY) src/fetch/pubmed_counts_by_gender.py

fetch_trends:
	$(PY) src/fetch/google_trends.py

fetch_cdc_example:
	$(PY) src/fetch/cdc_socrata_generic.py

transform:
	$(PY) src/transform/clean_merge_gendered.py

analyze:
	# analysis now happens via visualization and follow-up scripts; keep target for convenience
	$(PY) src/visualization/plot_correlations.py

viz:
	$(PY) src/visualization/corr_followups.py
	$(PY) src/visualization/gender_disparity_plots.py

build: fetch_pubmed fetch_trends transform analyze viz
