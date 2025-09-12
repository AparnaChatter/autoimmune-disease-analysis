import pandas as pd
from pathlib import Path
from utils.io import RAW, PROCESSED, write_csv
from utils.logging import get_logger
import re

disease_files = {
    'hashimoto': {'women': 'hashimoto_trends_women.csv', 'men': 'hashimoto_trends_men.csv'},
    'lupus': {'women': 'lupus_trends_women.csv', 'men': 'lupus_trends_men.csv'},
    'ms': {'women': 'ms_trends_women.csv', 'men': 'ms_trends_men.csv'},
    'ra': {'women': 'ra_trends_women.csv', 'men': 'ra_trends_men.csv'},
    # sjogren omitted (no gendered trends)
}

def clean_trends_csv(path, disease, gender):
    # Skip first two lines, extract month and value, standardize columns
    df = pd.read_csv(path, skiprows=2)
    df.columns = ['month', 'interest']
    df['disease_id'] = disease
    df['gender'] = gender
    # Remove trailing text from interest col if present
    df['interest'] = pd.to_numeric(df['interest'], errors='coerce')
    # Drop rows with missing/NaN
    df = df.dropna(subset=['interest'])
    return df

def combine_trends():
    frames = []
    for disease, genders in disease_files.items():
        for gender, fname in genders.items():
            fpath = RAW / fname
            if fpath.exists():
                frames.append(clean_trends_csv(fpath, disease, gender))
    all_trends = pd.concat(frames, ignore_index=True)
    # Convert month to datetime, extract year
    all_trends['month'] = pd.to_datetime(all_trends['month'], errors='coerce')
    all_trends = all_trends.dropna(subset=['month'])
    all_trends['year'] = all_trends['month'].dt.year
    # Aggregate to yearly mean
    yearly = (all_trends.groupby(['year','disease_id','gender'], as_index=False)
                        .agg(interest=('interest','mean')))
    return yearly

def load_pubmed():
    p = RAW / 'pubmed_counts_by_gender.csv'
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

def load_cdc(disease):
    # CDC WONDER files are named like lupus_wonder_by_sex.csv
    fpath = RAW / f'{disease}_wonder_by_sex.csv'
    if not fpath.exists():
        return pd.DataFrame()
    # Read CSV, skip any trailing non-data rows
    df = pd.read_csv(fpath, dtype=str)
    df = df.rename(columns=lambda x: x.strip().lower().replace(' ', '_'))
    # Remove rows where year is not a digit (skips totals, notes, etc.)
    df = df[df['year'].apply(lambda x: str(x).isdigit() if pd.notnull(x) else False)]
    df = df[df['sex'].isin(['Male','Female'])]
    df['year'] = df['year'].astype(int)
    df['disease_id'] = disease
    df['gender'] = df['sex'].map({'Male':'men','Female':'women'})
    # Clean deaths and crude_rate columns: set to NaN if 'Suppressed' or contains 'Unreliable'
    def clean_num(val):
        if pd.isnull(val):
            return pd.NA
        if isinstance(val, str):
            if 'Suppressed' in val or 'Unreliable' in val:
                return pd.NA
            val = re.sub(r'[^0-9\.]+', '', val)
        try:
            return float(val)
        except:
            return pd.NA
    df['deaths'] = df['deaths'].apply(clean_num)
    df['population'] = pd.to_numeric(df['population'], errors='coerce')
    df['crude_rate'] = df['crude_rate'].apply(clean_num)
    keep = ['year','disease_id','gender','deaths','population','crude_rate']
    for col in keep:
        if col not in df.columns:
            df[col] = pd.NA
    return df[keep]

def main():
    logger = get_logger('clean_merge_gendered')
    trends = combine_trends()
    pubmed = load_pubmed()
    cdc_frames = [load_cdc(d) for d in disease_files.keys()]
    cdc_frames_nonempty = [df for df in cdc_frames if not df.empty]
    logger.info(f'PubMed shape: {pubmed.shape}')
    logger.info(f'Trends shape: {trends.shape}')
    logger.info(f'CDC frames: {[df.shape for df in cdc_frames]}')
    # Merge all three on year, disease_id, gender
    merged = pubmed.merge(trends, on=['year','disease_id','gender'], how='inner')
    logger.info(f'After PubMed+Trends merge: {merged.shape}')
    if cdc_frames_nonempty:
        cdc = pd.concat(cdc_frames_nonempty, ignore_index=True)
        logger.info(f'CDC concat shape: {cdc.shape}')
        merged = merged.merge(cdc, on=['year','disease_id','gender'], how='left')
        logger.info(f'After CDC merge: {merged.shape}')
    else:
        # Add CDC columns as NaN if not present
        for col in ['deaths','population','crude_rate']:
            if col not in merged.columns:
                merged[col] = pd.NA
        logger.warning('No CDC data found. Proceeding with PubMed and Trends only.')
    write_csv(merged, PROCESSED / 'merged_gendered_signals.csv')
    logger.info(f'Merged rows: {len(merged)}')

if __name__ == '__main__':
    main()
