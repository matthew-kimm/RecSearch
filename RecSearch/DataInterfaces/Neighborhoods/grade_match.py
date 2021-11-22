from RecSearch.DataInterfaces.Neighborhoods.Abstract import INeighborhoodGrade
import pandas as pd
import numpy as np


class IXGradeMatch(INeighborhoodGrade):
    def iget_neighborhood(self, who: dict, possible: pd.DataFrame, item_history_col: str, exact_grade: bool) -> list:
        df = possible
        who_grades = who[item_history_col]
        if not exact_grade:
            letter_grade_map = {4.0: 4.0, 3.7: 4.0,
                                3.3: 3.0, 3.0: 3.0, 2.7: 3.0,
                                2.3: 2.0, 2.0: 2.0, 1.7: 2.0,
                                1.3: 1.0, 1.0: 1.0,
                                0.0: 0.0}
            df[item_history_col] = df[item_history_col].apply(lambda x: {k: letter_grade_map[v]
                                                                         for k, v in x.items()})

        df['Common_GPA'] = df[item_history_col].apply(
            lambda other_grades: np.mean(list({x: other_grades[x] for x in other_grades.keys()
                                               if x in who_grades.keys() and other_grades[x] == who_grades[x]
                                               }.values())))
        df = df[df['Common_GPA'].notna()]
        # Common_GPA not used but provided as an example to show passing along neighbor attributes
        return self.to_dicts(df[['Common_GPA']].itertuples())
