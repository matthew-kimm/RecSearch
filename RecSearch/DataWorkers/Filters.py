from RecSearch.DataWorkers.Abstract import DataWorkers
from RecSearch.ExperimentSupport.ExperimentData import ExperimentData
import pandas as pd


class Filters(DataWorkers):
    """
    Filters class prepares a list of possible items (courses) to recommend.
    """
    # Configs inline with [[NAME]]
    @classmethod
    def set_config(cls):
        additional_config = {'required': {'precedence': {'validate': 'integer(default=10)'}}}
        cls.cfg = super().update_config(cls.cfg, additional_config)

    def __init__(self, name: str, data_worker_config: dict, Data: ExperimentData):
        self.class_name = self.get_classname()
        super().__init__(self.class_name, name, data_worker_config, Data)

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def get_filters(self, column_name: str, whos: pd.DataFrame, possible: pd.DataFrame,
                    parameters: dict) -> pd.DataFrame:
        """
        Get filter (list of items) for every id in whos.index
        :param column_name: output column name
        :param whos: who(s) [with related data] to iterate to get neighborhood
        :param possible: potential neighbors [with related data]
        :param parameters: additional parameters
        :return: dataframe with column containing list of ids of neighbors for each who in who(s)
        """
        df = pd.DataFrame(columns=[ckey := 'F__' + column_name])
        for who in whos.itertuples():
            df = df.append(pd.Series(data=[self.Interface.iget_filter(who._asdict(), possible, **parameters)], index=[ckey], name=who[0]))
        self.Interface.clean_up()
        return df

    def do_work(self):
        return self.get_filters(self.name, self.eval, self.train, self.parameters)


Filters.set_config()
