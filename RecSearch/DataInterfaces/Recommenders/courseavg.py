from RecSearch.DataInterfaces.Recommenders.Abstract import ICountRecommender
import pandas as pd


class IXCourseAvgRecommend(ICountRecommender):
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, n_column: str, ir_column: str, count: int, filter_name: str = None) -> list:
        f = self.get_filter(who, filter_name)
        df = self.get_reduced_df(who, possible, n_column)
        df[ir_column] = df[ir_column].apply(lambda x: [';'.join((str(k), str(v))) for k, v in x.items() if k not in f])
        df = df.explode(column=ir_column).dropna()
        if df.empty:
            return []
        else:
            df[['Item', 'Rating']] = df[ir_column].str.split(pat=';', expand=True)
            df['Rating'] = df['Rating'].astype(float)
            df = df.groupby(['Item']).agg(
                    MeanGPA=pd.NamedAgg('Rating', 'mean'),
                    Count=pd.NamedAgg('Rating', 'count')
                )
            df = df[df['Count'] >= count].sort_values(by='MeanGPA', ascending=False)
            return list(df.index.dropna())
