# Script to fetch and preprocess CDC data by sex for autoimmune diseases
# Placeholder: implement CDC data fetching and group by sex
def fetch_cdc_data():
    import requests
    import pandas as pd
    # CDC CDI Socrata API endpoint for arthritis
    url = "https://data.cdc.gov/resource/g4ie-h725.json"
    params = {
        "$where": "indicator='Arthritis among adults aged >= 18 years' AND sex in ('Male','Female')",
        "$limit": 50000
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data)
    # Keep only relevant columns
    df = df[["yearstart", "locationdesc", "sex", "data_value"]]
    df = df.rename(columns={"yearstart": "year", "locationdesc": "state", "data_value": "prevalence"})
    print(df.head())
    df.to_csv('data/processed/cdc_arthritis_by_gender.csv', index=False)
    print("Saved CDC arthritis prevalence by gender to data/processed/cdc_arthritis_by_gender.csv")

    # Placeholder for lupus mortality by sex (CDC WONDER or manual download)
    print("\nTo get lupus mortality by sex, use CDC WONDER: https://wonder.cdc.gov/ and export results by sex for ICD-10 code M32 (Systemic Lupus Erythematosus).\n")

if __name__ == "__main__":
    fetch_cdc_data()
