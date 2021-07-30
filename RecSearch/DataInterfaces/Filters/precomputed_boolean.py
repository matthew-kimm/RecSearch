from RecSearch.DataInterfaces.Filters.Abstract import IFilterFromFile
import pandas as pd


class IXPrePostFilter(IFilterFromFile):
    def iget_filter(self, who: dict, possible: pd.DataFrame, filter_file: str) -> list:
        filter_data = self.load_csv_cached(filter_file, 0)
        try:
            filter_list = filter_data.loc[who['Index']][0]
        except ValueError:
            filter_list = []
        return filter_list
