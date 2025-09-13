"""Generate follow-up visualizations and Granger tests for top correlated pairs.

Outputs (in reports/):
- z_timeseries_{disease}_{gender}.png
- ccf_{disease}_{gender}.png
- granger_{disease}_{gender}.txt
- corr_followups_summary.md
"""
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy import stats


def zscore(s):
    return (s - s.mean()) / s.std() if s.std() and not s.std()==0 else (s - s.mean())


def ccf(a, b, maxlag=5):
    # compute pearson r for lags -maxlag..maxlag where positive lag means a leads b by lag
    res = {}
    for lag in range(-maxlag, maxlag+1):
        if lag < 0:
            # b leads a by |lag|
            la = a[-lag:].reset_index(drop=True)
            lb = b[:len(b)+lag].reset_index(drop=True)
        elif lag > 0:
            la = a[:-lag].reset_index(drop=True)
            lb = b[lag:].reset_index(drop=True)
        else:
            la = a.reset_index(drop=True)
            lb = b.reset_index(drop=True)
        # trim to same length if necessary
        if len(la) == 0 or len(lb) == 0:
            res[lag] = np.nan
            continue
        if len(la) != len(lb):
            m = min(len(la), len(lb))
            la = la[:m]
            lb = lb[:m]
        if len(la) < 3:
            res[lag] = np.nan
            continue
        try:
            res[lag] = stats.pearsonr(la, lb)[0]
        except Exception:
            res[lag] = np.nan
    return res


def main():
    rpt = Path('reports')
    rpt.mkdir(exist_ok=True)
    cs = pd.read_csv(rpt / 'correlation_summary.csv')
    merged = pd.read_csv(Path('data/processed/merged_gendered_signals.csv'))
    # pick top pairs (exclude ALL) with n>=5 by abs pearson_r
    cand = cs[(cs['disease_id']!='ALL') & (cs['n']>=5)].copy()
    cand['absr'] = cand['pearson_r'].abs()
    top = cand.sort_values('absr', ascending=False).drop_duplicates(subset=['disease_id','gender','pair']).head(6)
    # choose up to 3 unique disease/gender combos (prefer highest absr)
    combos = []
    for _, row in top.iterrows():
        key = (row['disease_id'], row['gender'])
        if key not in combos:
            combos.append(key)
        if len(combos) >= 3:
            break

    md_lines = ['# Correlation follow-up summary', '']
    for disease, gender in combos:
        sub = merged[(merged['disease_id']==disease)&(merged['gender']==gender)].sort_values('year')
        if sub.empty:
            continue
        years = sub['year'].astype(int)
        A = zscore(pd.to_numeric(sub['interest'], errors='coerce')) if 'interest' in sub.columns else None
        B = zscore(pd.to_numeric(sub['count'], errors='coerce')) if 'count' in sub.columns else None
        C = zscore(pd.to_numeric(sub['deaths'], errors='coerce')) if 'deaths' in sub.columns else None

        # find best lag for interest-deaths or count-deaths pairs from cs
        # we'll align the variable (A or B) forward by lag that maximizes abs r with deaths
        best_info = cs[(cs['disease_id']==disease)&(cs['gender']==gender)&(cs['pair']=='interest-deaths')]
        best_count_info = cs[(cs['disease_id']==disease)&(cs['gender']==gender)&(cs['pair']=='count-deaths')]
        best_lag = int(best_info.loc[best_info['pearson_r'].abs().idxmax()]['lag']) if (not best_info.empty and best_info['pearson_r'].notna().any()) else 0
        best_count_lag = int(best_count_info.loc[best_count_info['pearson_r'].abs().idxmax()]['lag']) if (not best_count_info.empty and best_count_info['pearson_r'].notna().any()) else 0

        # Time series overlay (z-score). Also show shifted series by best lag.
        plt.figure(figsize=(10,4))
        if A is not None:
            plt.plot(years, A, label='interest (z)')
        if B is not None:
            plt.plot(years, B, label='count (z)')
        if C is not None:
            plt.plot(years, C, label='deaths (z)')
        # shifted versions
        if C is not None and A is not None and best_lag>0:
            plt.plot(years, pd.concat([pd.Series([np.nan]*best_lag), A[:-best_lag].reset_index(drop=True)]), '--', label=f'interest shifted +{best_lag}')
        if C is not None and B is not None and best_count_lag>0:
            plt.plot(years, pd.concat([pd.Series([np.nan]*best_count_lag), B[:-best_count_lag].reset_index(drop=True)]), '--', label=f'count shifted +{best_count_lag}')
        plt.title(f'Z-scored time series: {disease} - {gender}')
        plt.xlabel('Year')
        plt.legend()
        plt.tight_layout()
        fn = rpt / f'z_timeseries_{disease}_{gender}.png'
        plt.savefig(fn)
        plt.close()

        md_lines.append(f'## {disease} {gender}')
        md_lines.append(f'Z-scored overlay: `{fn.name}`')

        # CCF between interest/count and deaths
        if C is not None and A is not None:
            res = ccf(A.dropna().reset_index(drop=True), C.dropna().reset_index(drop=True), maxlag=5)
            plt.figure()
            lags = sorted(res.keys())
            vals = [res[l] for l in lags]
            # matplotlib versions differ; avoid use_line_collection kwarg
            plt.stem(lags, vals)
            plt.axhline(0, color='k', linewidth=0.5)
            plt.title(f'CCF interest -> deaths: {disease} {gender}')
            plt.xlabel('lag (years, positive = interest leads)')
            plt.ylabel('Pearson r')
            plt.tight_layout()
            fn2 = rpt / f'ccf_interest_deaths_{disease}_{gender}.png'
            plt.savefig(fn2)
            plt.close()
            md_lines.append(f'CCF plot: `{fn2.name}`')

        if C is not None and B is not None:
            res = ccf(B.dropna().reset_index(drop=True), C.dropna().reset_index(drop=True), maxlag=5)
            plt.figure()
            lags = sorted(res.keys())
            vals = [res[l] for l in lags]
            plt.stem(lags, vals)
            plt.axhline(0, color='k', linewidth=0.5)
            plt.title(f'CCF count -> deaths: {disease} {gender}')
            plt.xlabel('lag (years, positive = count leads)')
            plt.ylabel('Pearson r')
            plt.tight_layout()
            fn3 = rpt / f'ccf_count_deaths_{disease}_{gender}.png'
            plt.savefig(fn3)
            plt.close()
            md_lines.append(f'CCF plot: `{fn3.name}`')

        # Granger causality tests (if statsmodels available)
        try:
            from statsmodels.tsa.stattools import grangercausalitytests
            granger_txt = rpt / f'granger_{disease}_{gender}.txt'
            with open(granger_txt, 'w') as fh:
                if C is not None and A is not None:
                    # test if interest Granger-causes deaths: format (deaths, interest)
                    data = pd.concat([C.fillna(method='ffill').dropna().reset_index(drop=True), A.fillna(method='ffill').dropna().reset_index(drop=True)], axis=1)
                    if len(data) >= 6:
                        fh.write('Granger test: interest -> deaths\n')
                        try:
                            grangercausalitytests(data.iloc[:, [0,1]], maxlag=3, verbose=False)
                            fh.write('Completed Granger tests (see console for detailed output)\n')
                        except Exception as e:
                            fh.write('Granger test failed: '+str(e)+"\n")
                if C is not None and B is not None:
                    data = pd.concat([C.fillna(method='ffill').dropna().reset_index(drop=True), B.fillna(method='ffill').dropna().reset_index(drop=True)], axis=1)
                    if len(data) >= 6:
                        fh.write('Granger test: count -> deaths\n')
                        try:
                            grangercausalitytests(data.iloc[:, [0,1]], maxlag=3, verbose=False)
                            fh.write('Completed Granger tests (see console for detailed output)\n')
                        except Exception as e:
                            fh.write('Granger test failed: '+str(e)+"\n")
            md_lines.append(f'Granger results: `{granger_txt.name}`')
        except Exception as e:
            md_lines.append(f'Granger test skipped (statsmodels missing or failed): {e}')

    # write markdown summary
    (rpt / 'corr_followups_summary.md').write_text('\n'.join(md_lines))
    print('Generated follow-up plots and summary in reports/')


if __name__ == '__main__':
    main()
