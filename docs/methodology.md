# Methodology

We combine three signal types:

1. **Research attention**: PubMed yearly counts using E-utilities for MeSH terms (e.g., "Systemic Lupus Erythematosus").
2. **Public awareness**: Google Trends search interest (worldwide, 2004–present).
3. **Prevalence/burden**: Plug-in CSVs from CDC Socrata or GBD (manual download), ideally stratified by sex.

We compute:

- Female:male **prevalence ratios** (where data available).
- **Attention–burden gap**: normalized PubMed/Trends vs prevalence/DALYs.

Caveats:

- Publication counts reflect research output, not disease rates.
- Trends reflect search behavior, not incidence.
- Always annotate figures with data source and year.
