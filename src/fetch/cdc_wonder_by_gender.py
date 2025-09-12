import requests
import yaml
import pandas as pd

# Map your diseases to ICD-10 codes for CDC WONDER
ICD10_MAP = {
    "sle": "M32",  # Systemic Lupus Erythematosus
    "ms": "G35",   # Multiple Sclerosis
    "hashimoto": "E06.3",  # Hashimoto Thyroiditis (may not be available as separate cause)
    "ra": "M05,M06",  # Rheumatoid Arthritis (may need to split)
    "sjogren": "M35.0"  # Sjögren Syndrome
}

with open("src/config/diseases.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

years = list(range(cfg["years"]["start"], cfg["years"]["end"] + 1))
results = []

for disease in cfg["diseases"]:
    disease_id = disease["id"]
    icd10 = ICD10_MAP.get(disease_id)
    if not icd10:
        print(f"No ICD-10 code for {disease['name']}, skipping.")
        continue
    for year in years:
        url = "https://wonder.cdc.gov/api/v1/ucd"
        params = {
            "icd10": icd10,
            "group_by": "sex",
            "year": year
        }
        try:
            r = requests.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            for row in data.get('results', []):
                row['disease_id'] = disease_id
                row['disease_name'] = disease['name']
                row['year'] = year
                results.append(row)
        except Exception as e:
            print(f"Error fetching {disease['name']} {year}: {e}")

if results:
    df = pd.DataFrame(results)
    df.to_csv("data/processed/cdc_wonder_by_gender.csv", index=False)
    print("Saved CDC WONDER mortality by gender to data/processed/cdc_wonder_by_gender.csv")
else:
    print("No results fetched.")
