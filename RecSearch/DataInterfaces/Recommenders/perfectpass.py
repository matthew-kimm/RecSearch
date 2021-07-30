from RecSearch.DataInterfaces.Recommenders.Abstract import IDummyRecommender1Parameter
import pandas as pd


class IXPerfectRecommender(IDummyRecommender1Parameter):
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, ir_column: str, perfect_rating: float) -> list:
        return [key for key, value in who[ir_column].items() if value >= perfect_rating]
