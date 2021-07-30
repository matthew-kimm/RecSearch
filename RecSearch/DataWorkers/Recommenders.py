from RecSearch.DataWorkers.Abstract import DataWorkers
from RecSearch.ExperimentSupport.ExperimentData import ExperimentData
import pandas as pd


class Recommenders(DataWorkers):
    """
    Recommenders class creates recommender data.
    """
    # Configs inline with [[NAME]]
    @classmethod
    def set_config(cls):
        additional_config = {'required': {'precedence': {'validate': 'integer(default=30)'}}}
        cls.cfg = super().update_config(cls.cfg, additional_config)

    def __init__(self, name: str, data_worker_config: dict, Data: ExperimentData):
        self.class_name = self.get_classname()
        super().__init__(self.class_name, name, data_worker_config, Data)

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def get_recommendations(self, column_name: str, whos: pd.DataFrame, possible: pd.DataFrame,
                            parameters: dict) -> pd.DataFrame:
        """
        Get recommendations (list of items) for every id in whos.index
        :param column_name: output column name
        :param whos: who(s) [with related data] to get recommendation
        :param possible: potential neighbors to offer recommendation [with related data]
        :param parameters: additional parameters
        :return: dataframe with column containing list of ids of neighbors for each who in who(s)
        """
        df = pd.DataFrame(columns=[ckey := 'R__' + column_name])
        for who in whos.itertuples():
            df = df.append(pd.Series(data=[self.Interface.iget_recommendation(who._asdict(), possible, **parameters)], index=[ckey],
                                     name=who[0]))
        return df

    def do_work(self):
        return self.get_recommendations(self.name, self.eval, self.train, self.parameters)


Recommenders.set_config()
