# Script to visualize gender disparity across CDC, PubMed, and Google Trends data
# Placeholder: implement visualization logic
import pandas as pd
import matplotlib.pyplot as plt

def plot_gender_disparity():
    import seaborn as sns
    from pathlib import Path

    # Load merged data
    df = pd.read_csv(Path(__file__).parents[2] / 'data' / 'processed' / 'merged_gendered_signals.csv')

    # Drop rows with all-NaN CDC columns for CDC-specific analyses
    cdc_cols = ['deaths', 'population', 'crude_rate']
    df_cdc = df.dropna(subset=cdc_cols, how='all')

    # Correlation matrix (all numeric columns)
    corr = df[['count', 'interest', 'deaths', 'population', 'crude_rate']].corr()
    print('Correlation matrix:')
    print(corr)

    # Save correlation heatmap
    plt.figure(figsize=(6,5))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix: PubMed, Trends, CDC')
    plt.tight_layout()
    Path('reports').mkdir(exist_ok=True)
    plt.savefig('reports/correlation_heatmap.png')
    plt.close()

    # Scatter plots: PubMed vs Trends, PubMed vs CDC, Trends vs CDC
    for disease in df['disease_id'].unique():
        for gender in df['gender'].unique():
            sub = df[(df['disease_id']==disease) & (df['gender']==gender)]
            label = f"{disease.capitalize()} - {gender.capitalize()}"
            # PubMed vs Trends
            plt.figure()
            sns.scatterplot(x='count', y='interest', data=sub)
            plt.title(f'PubMed vs Trends: {label}')
            plt.xlabel('PubMed Publication Count')
            plt.ylabel('Google Trends Interest')
            plt.tight_layout()
            plt.savefig(f'reports/scatter_pubmed_trends_{disease}_{gender}.png')
            plt.close()
            # PubMed vs CDC (deaths)
            if 'deaths' in sub.columns:
                plt.figure()
                sns.scatterplot(x='count', y='deaths', data=sub)
                plt.title(f'PubMed vs CDC Deaths: {label}')
                plt.xlabel('PubMed Publication Count')
                plt.ylabel('CDC Deaths')
                plt.tight_layout()
                plt.savefig(f'reports/scatter_pubmed_cdc_{disease}_{gender}.png')
                plt.close()
            # Trends vs CDC (deaths)
            if 'deaths' in sub.columns:
                plt.figure()
                sns.scatterplot(x='interest', y='deaths', data=sub)
                plt.title(f'Trends vs CDC Deaths: {label}')
                plt.xlabel('Google Trends Interest')
                plt.ylabel('CDC Deaths')
                plt.tight_layout()
                plt.savefig(f'reports/scatter_trends_cdc_{disease}_{gender}.png')
                plt.close()

    # Time series plots for each signal
    groups = df.groupby(['disease_id','gender'])
    for (disease, gender), sub in groups:
        plt.figure(figsize=(10,5))
        plt.plot(sub['year'], sub['count'], label='PubMed')
        plt.plot(sub['year'], sub['interest'], label='Trends')
        if 'deaths' in sub.columns:
            plt.plot(sub['year'], sub['deaths'], label='CDC Deaths')
        plt.title(f'Time Series: {disease.capitalize()} - {gender.capitalize()}')
        plt.xlabel('Year')
        plt.ylabel('Value')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'reports/timeseries_{disease}_{gender}.png')
        plt.close()

    print('All visualizations and correlation studies saved in the reports/ directory.')

if __name__ == "__main__":
    plot_gender_disparity()
