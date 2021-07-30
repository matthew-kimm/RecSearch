from RecSearch.DataWorkers.Abstract import DataWorkers
from RecSearch.ExperimentSupport.ExperimentData import ExperimentData
import pandas as pd


class Metrics(DataWorkers):
    """
    Metric class adds metric data.
    """
    # Configs inline with [[NAME]]
    @classmethod
    def set_config(cls):
        additional_config = {'required': {'precedence': {'validate': 'integer(default=40)'}}}
        cls.cfg = super().update_config(cls.cfg, additional_config)

    def __init__(self, name: str, data_worker_config: dict, Data: ExperimentData):
        self.class_name = self.get_classname()
        super().__init__(self.class_name, name, data_worker_config, Data)

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def get_metrics(self, column_name: str, whos: pd.DataFrame, parameters: dict) -> pd.DataFrame:
        """
        Get neighborhood (list of ids) for every id in whos.index
        :param column_name: output column name
        :param whos: who(s) [with related data] to iterate to get metrics
        :param parameters: additional parameters
        :return: dataframe with column containing metric data for each who in who(s)
        """
        df = pd.DataFrame()
        for who in whos.itertuples():
            data = self.Interface.iget_metric(who._asdict(), **parameters)
            df = df.append(pd.Series(data=[v for v in data.values()],
                                     index=['M__' + column_name + k for k in data.keys()], name=who[0]))
        return df

    def do_work(self):
        return self.get_metrics(self.name, self.eval, self.parameters)


Metrics.set_config()
