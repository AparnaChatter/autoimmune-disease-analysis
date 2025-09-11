# Autoimmune Gender Disparities: A Data Analysis Project

**Goal:** quantify and visualize how autoimmune diseases disproportionately affect women, using public data and reproducible code.

## Research questions

1. How does the **female:male prevalence ratio** vary across autoimmune diseases?
2. How has attention (research publications, search interest) trended over time relative to burden?
3. Where are the **largest gaps** between research interest and estimated burden?

## Data sources (no paid keys)

- **PubMed E-utilities**: yearly article counts by disease (proxy for research attention).
- **Google Trends**: search interest (proxy for public awareness).
- **CDC Socrata endpoints** (optional; examples & template provided) for US prevalence where available (e.g., arthritis-related indicators).

> ⚠️ Prevalence by sex for every autoimmune disease is not uniformly available via one API. This repo gives you (a) working pipelines (PubMed/Trends) and (b) a CDC Socrata template you can point at specific datasets that report sex-stratified estimates.

## Quickstart

```bash
# 1) clone and enter
git clone https://github.com/<you>/autoimmune-gender-disparities.git
cd autoimmune-gender-disparities

# 2) set up Python env
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3) configure env (optional)
cp .env.example .env
# (Optional) fill in GOOGLE_TRENDS_PROXY or NCBI_API_KEY if you have one

# 4) fetch data
make fetch_pubmed
make fetch_trends

# 5) clean + merge + analyze + visualize
make build

# 6) open notebook
jupyter lab

```
