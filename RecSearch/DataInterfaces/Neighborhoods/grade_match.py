from RecSearch.DataInterfaces.Neighborhoods.Abstract import INeighborhoodGrade
import pandas as pd
import numpy as np


class IXGradeMatch(INeighborhoodGrade):
    def iget_neighborhood(self, who: dict, possible: pd.DataFrame, item_history_col: str) -> list:
        df = possible
        who_grades = who[item_history_col]
        df['Common_GPA'] = df[item_history_col].apply(
            lambda other_grades: np.mean(list({x: other_grades[x] for x in other_grades.keys()
                                               if x in who_grades.keys() and other_grades[x] == who_grades[x]
                                               }.values())))
        df = df[df['Common_GPA'].notna()]
        return self.to_dicts(df[['Common_GPA']].itertuples())
