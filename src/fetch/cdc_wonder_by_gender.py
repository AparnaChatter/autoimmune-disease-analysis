import requests
import pandas as pd
import xml.etree.ElementTree as ET

# Map your diseases to ICD-10 codes for CDC WONDER
ICD10_MAP = {
    "sle": "M32",  # Systemic Lupus Erythematosus
    "ms": "G35",   # Multiple Sclerosis
    "hashimoto": "E06.3",  # Hashimoto Thyroiditis (may not be available as separate cause)
    "ra": "M05,M06",  # Rheumatoid Arthritis (may need to split)
    "sjogren": "M35.0"  # Sjögren Syndrome
}

WONDER_URL = "https://wonder.cdc.gov/controller/datarequest/D76"

def build_request_xml(icd_codes: str) -> str:
    """
    Build XML request for WONDER D76 mortality database
    Group by Sex and Year, filter by ICD-10 codes
    """
    xml = f"""<request-parameters>
  <parameter>
    <name>accept_datause_restrictions</name>
    <value>true</value>
  </parameter>
  <parameter>
    <name>B_1</name>
    <value>D76.V1-level1</value> <!-- Year -->
  </parameter>
  <parameter>
    <name>B_2</name>
    <value>D76.V7</value> <!-- Sex -->
  </parameter>
  <parameter>
    <name>F_D76.V2</name>
    <value>{icd_codes}</value> <!-- ICD-10 filter -->
  </parameter>
  <parameter>
    <name>M_1</name>
    <value>D76.M1</value> <!-- Number of deaths -->
  </parameter>
  <parameter>
    <name>O_ucd</name>
    <value>D76.V2</value> <!-- Underlying cause of death field -->
  </parameter>
  <parameter>
    <name>O_show_suppressed</name>
    <value>true</value>
  </parameter>
  <parameter>
    <name>O_show_zeros</name>
    <value>true</value>
  </parameter>
  <parameter>
    <name>O_show_totals</name>
    <value>true</value>
  </parameter>
</request-parameters>"""
    return xml

def query_wonder(icd_codes: str) -> pd.DataFrame:
    """
    Query CDC WONDER API for ICD-10 codes.
    Returns Pandas DataFrame with columns: Year, Sex, Deaths
    """
    xml_request = build_request_xml(icd_codes)
    response = requests.post(
        WONDER_URL,
        data={"request_xml": xml_request, "accept_datause_restrictions": "true"}
    )
    response.raise_for_status()

    root = ET.fromstring(response.text)

    # Navigate to data-table rows
    data_table = root.find(".//data-table")
    rows = []
    for row in data_table.findall("r"):
        cells = [c.text for c in row.findall("c")]
        rows.append(cells)

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=["Year", "Sex", "Deaths"])
    return df

if __name__ == "__main__":
    results = {}
    for disease, codes in ICD10_MAP.items():
        try:
            df = query_wonder(codes)
            results[disease] = df
            print(f"\n=== {disease.upper()} ===")
            print(df.head())
        except Exception as e:
            print(f"Failed for {disease}: {e}")
