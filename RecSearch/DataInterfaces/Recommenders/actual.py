from RecSearch.DataInterfaces.Recommenders.Abstract import IDummyRecommender
import pandas as pd


class IXActualRated(IDummyRecommender):
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, ir_column: str, filter_name: str = None) -> list:
        f = self.get_filter(who, filter_name)
        actual = [course for course in who[ir_column].keys() if course not in f]
        return actual
