import pandas as pd
import matplotlib.pyplot as plt


def plot_evl(comparer: str):
    title = 'Pass Rate by Neighbor Grade Match' if comparer == 'pass'\
        else 'Matched Courses by Neighbor Grade Match'
    df = pd.read_csv(f'./Summary/evl_{comparer}/all_rename.csv')
    df = df.groupby('Recommender')['Value'].agg('mean')
    actual = df.loc[['Actual', 'ActualFilter']]
    df = df.drop(['Actual', 'ActualFilter'])
    df = df.reset_index()
    df['Neighborhood'] = df['Recommender'].apply(lambda x: x.split('_')[1])
    df['Recommender'] = df['Recommender'].apply(lambda x: x.split('_')[0])
    df = df.groupby(['Recommender', 'Neighborhood'])['Value'].agg('mean').unstack().reset_index()

    if comparer == 'count':
        df.plot(x='Recommender', kind='bar', legend=True, color=['#545454', '#B5B5B5'], title=title)
    elif comparer == 'pass':
        df.plot(x='Recommender', kind='bar', legend=True, color=['#545454', '#B5B5B5'], title=title,
                ylim=(0.8, 1.0))

    plt.xticks(rotation=45)
    plt.ylabel('Pass Rate' if comparer == 'pass' else 'Count Recommended Courses Match Actual Courses')
    plt.savefig(f'{comparer}_by_grade_match.pdf', bbox_inches='tight')


plot_evl('pass')
plot_evl('count')
