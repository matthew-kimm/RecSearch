from RecSearch.DataInterfaces.Filters.Abstract import IFilterFromFileParameter
from typing import Union
import pandas as pd
import ast


class IXFilterOnFly(IFilterFromFileParameter):
    def iget_filter(self, who: dict, possible: pd.DataFrame, history_col: str, filter_file: Union[str, pd.DataFrame],
                    passing_grade: float) -> list:
        if type(filter_file) == str:
            data = pd.read_csv(filter_file, index_col=0)
            ast_data = data.loc['AST_Literal_Eval']
            data = data.drop('AST_Literal_Eval')
            for col, value in ast_data.items():
                if int(value):
                    data[col] = data[col].apply(lambda x: ast.literal_eval(x))
        else:
            data = filter_file
        data['Condition'] = data['Condition'].fillna('')
        condition_vector = pd.Series(data=0, index=data.index)
        history = who[history_col]

        filter_list = []
        for course, grade in history.items():
            try:
                filter_list += data.loc[course]['Implies']
            except KeyError:
                pass
            if grade >= passing_grade:
                filter_list += [course, ]
        filter_list = list(set(filter_list))
        for course in filter_list:
            try:
                condition_vector.loc[course] = 1
            except KeyError:
                condition_vector = condition_vector.append(pd.Series(1, index=[course]))

        for course in condition_vector.index:
            try:
                replace = sorted(data.loc[course]['Replace'], reverse=True)
                condition = data.loc[course]['Condition']
            except KeyError:
                continue
            if not condition:
                continue
            else:
                for rep in replace:
                    try:
                        condition = condition.replace(rep, str(condition_vector.loc[rep]))
                    except KeyError:
                        condition = condition.replace(rep, '0')
                if set(condition).issubset({'0', '1', '&', '|', '(', ')'}):
                    if not eval(condition):
                        filter_list += [course, ]
                else:
                    print(condition)

        filter_list = list(set(filter_list))
        return filter_list
