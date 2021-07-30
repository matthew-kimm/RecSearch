from RecSearch.DataWorkers.Abstract import DataWorkers
from RecSearch.ExperimentSupport.ExperimentData import ExperimentData
import pandas as pd

class Comparers(DataWorkers):
    """
    Comparer class adds comparison data (between metrics).
    """
    # Configs inline with [[NAME]]
    @classmethod
    def set_config(cls):
        additional_config = {'required': {'precedence': {'validate': 'integer(default=50)'}}}
        cls.cfg = super().update_config(cls.cfg, additional_config)

    def __init__(self, name: str, data_worker_config: dict, Data: ExperimentData):
        self.class_name = self.get_classname()
        super().__init__(self.class_name, name, data_worker_config, Data)

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def get_comparers(self, column_name: str, whos: pd.DataFrame, parameters: dict) -> pd.DataFrame:
        """
        Get neighborhood (list of ids) for every id in whos.index
        :param column_name: output column name
        :param whos: who(s) [with related data] to iterate to get metrics
        :param parameters: additional parameters
        :return: dataframe with column containing metric data for each who in who(s)
        """
        df = pd.DataFrame()
        for who in whos.itertuples():
            data = self.Interface.iget_comparer(who._asdict(), **parameters)
            df = df.append(pd.Series(data=[v for v in data.values()],
                                     index=['C__' + column_name + k for k in data.keys()], name=who[0]))
        return df

    def do_work(self):
        return self.get_comparers(self.name, self.eval, self.parameters)


Comparers.set_config()
