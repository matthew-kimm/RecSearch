from RecSearch.DataInterfaces.Recommenders.Abstract import IRecommender
import pandas as pd


class IXPopularRecommend(IRecommender):
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, n_column: str, ir_column: str, filter_name: str = None) -> list:
        f = self.get_filter(who, filter_name)
        df = self.get_reduced_df(who, possible, n_column)
        courses = df[ir_column].apply(lambda x: [key for key in x.keys() if key not in f]).explode().dropna()
        courses = courses.value_counts()
        return list(courses.index)