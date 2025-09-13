"""Plot correlation summary outputs saved at reports/correlation_summary.csv

Produces:
- reports/corr_heatmap_overall_lag0.png
- reports/corr_heatmap_{disease}_{gender}.png (pearson r heatmap: pairs x lag)
- reports/corr_lags_{disease}_{gender}.png (line plots of pearson r vs lag for each pair)
- reports/corr_top_associations.png (top abs r barplot across disease/gender)
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def main():
    rpt = Path('reports')
    rpt.mkdir(exist_ok=True)
    path = rpt / 'correlation_summary.csv'
    if not path.exists():
        print('correlation_summary.csv not found at', path)
        return

    df = pd.read_csv(path)
    # ensure numeric
    df['pearson_r'] = pd.to_numeric(df['pearson_r'], errors='coerce')
    df['spearman_r'] = pd.to_numeric(df['spearman_r'], errors='coerce')
    df['n'] = pd.to_numeric(df['n'], errors='coerce')

    # Overall heatmap at lag 0
    overall0 = df[(df['disease_id']=='ALL') & (df['lag']==0)].set_index('pair')
    if not overall0.empty:
        vals = overall0['pearson_r'].reindex(['interest-count','interest-deaths','count-deaths'])
        plt.figure(figsize=(6,2))
        sns.heatmap(vals.to_frame().T, annot=True, cmap='coolwarm', center=0, fmt='.2f')
        plt.title('Overall Pearson r (lag=0)')
        plt.tight_layout()
        plt.savefig(rpt / 'corr_heatmap_overall_lag0.png')
        plt.close()

    # Per disease/gender: pivot lag x pair
    diseases = sorted(df['disease_id'].unique())
    genders = sorted(df['gender'].unique())
    plots_made = 0
    for disease in diseases:
        if disease == 'ALL':
            continue
        for gender in genders:
            sub = df[(df['disease_id']==disease) & (df['gender']==gender)]
            if sub.empty:
                continue
            pivot = sub.pivot(index='lag', columns='pair', values='pearson_r')
            if pivot.dropna(how='all').empty:
                continue
            # Heatmap of r across lags
            plt.figure(figsize=(8, max(2, 0.6 * pivot.shape[1])))
            sns.heatmap(pivot.T, annot=True, cmap='coolwarm', center=0, fmt='.2f')
            plt.title(f'Pearson r by lag — {disease} ({gender})')
            plt.ylabel('pair')
            plt.xlabel('lag (years)')
            plt.tight_layout()
            fn1 = rpt / f'corr_heatmap_{disease}_{gender}.png'
            plt.savefig(fn1)
            plt.close()

            # Line plot of r vs lag for each pair
            plt.figure(figsize=(6,3))
            for col in pivot.columns:
                plt.plot(pivot.index, pivot[col], marker='o', label=col)
            plt.axhline(0, color='k', linewidth=0.5)
            plt.title(f'Pearson r vs lag — {disease} ({gender})')
            plt.xlabel('lag (years)')
            plt.ylabel('Pearson r')
            plt.legend()
            plt.tight_layout()
            fn2 = rpt / f'corr_lags_{disease}_{gender}.png'
            plt.savefig(fn2)
            plt.close()
            plots_made += 1

    # Top associations barplot (absolute r) for lag with max abs r per pair/disease/gender
    pick = df[df['disease_id'] != 'ALL'].copy()
    # For each disease/gender/pair select row with max abs pearson_r
    pick['absr'] = pick['pearson_r'].abs()
    best = pick.sort_values(['disease_id','gender','pair','absr'], ascending=[True,True,True,False])
    best = best.groupby(['disease_id','gender','pair']).first().reset_index()
    # filter n>=5 to exclude tiny samples
    best = best[best['n']>=5]
    if not best.empty:
        best['label'] = best['disease_id'] + '_' + best['gender'] + '_' + best['pair']
        best_sorted = best.sort_values('absr', ascending=False).head(30)
        plt.figure(figsize=(8, max(4, 0.2*len(best_sorted))))
        sns.barplot(x='pearson_r', y='label', data=best_sorted, palette='vlag')
        plt.title('Top associations (by abs Pearson r, n>=5)')
        plt.xlabel('Pearson r')
        plt.tight_layout()
        plt.savefig(rpt / 'corr_top_associations.png')
        plt.close()

    print(f'Plotted {plots_made} disease/gender correlation figures and summary plots in {rpt}/')


if __name__ == '__main__':
    main()
