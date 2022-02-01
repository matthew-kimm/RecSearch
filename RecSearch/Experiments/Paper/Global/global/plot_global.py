import pandas as pd
import matplotlib.pyplot as plt


def plot_global(comparer: str):
    title = 'Pass Rate by Recommender (Global)' if comparer == 'pass' else\
        'Matched Courses by Recommender (Global)'
    df = pd.read_csv(f'./Summary/global_{comparer}/all_rename.csv')
    df = df.groupby('Recommender')['Value'].agg('mean')
    df = df.reset_index()
    df = df.sort_values('Value')
    df['Value'] = df['Value']
    if comparer == 'count':
        df.plot(x='Recommender', kind='bar', color='#545454', legend=False)
    elif comparer == 'pass':
        df.plot(x='Recommender', kind='bar', color='#545454', ylim=(0.8, 1.0), legend=False)

    plt.title(title)
    plt.xticks(rotation=45)
    plt.ylabel('Pass Rate' if comparer == 'pass' else 'Count Recommended Courses Match Actual Courses')
    plt.savefig(f'{comparer}_by_global.pdf', bbox_inches='tight')
    plt.clf()


plot_global('pass')
plot_global('count')