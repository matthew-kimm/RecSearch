from RecSearch.DataWorkers.Abstract import DataWorkers
from RecSearch.ExperimentSupport.ExperimentData import ExperimentData

import pandas as pd


class Neighborhoods(DataWorkers):
    """
    Neighborhoods class creates neighborhood data.
    """
    # Configs inline with [[NAME]]
    @classmethod
    def set_config(cls):
        additional_config = {'required': {'min_neighbors': {'doc': 'Minimum num neighbors for neighborhood',
                                                            'input': 'text()',
                                                            'validate': 'integer(min=0, default=0)'
                                                            },
                                          'precedence': {'validate': 'integer(default=20)'}
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    def __init__(self, name: str, data_worker_config: dict, Data: ExperimentData):
        self.class_name = self.get_classname()
        super().__init__(self.class_name, name, data_worker_config, Data)

    @classmethod
    def get_classname(cls):
        return cls.__name__

    def check_min(self, column_name: str, df: pd.DataFrame):
        ncount = self.min_neighbors
        df[column_name] = df[column_name].apply(lambda x: x if len(x) >= ncount else [])
        return df

    def get_neighborhoods(self, column_name: str, whos: pd.DataFrame, possible: pd.DataFrame,
                          parameters: dict) -> pd.DataFrame:
        """
        Get neighborhood (list of ids) for every id in whos.index
        :param column_name: output column name
        :param whos: who(s) [with related data] to iterate to get neighborhood
        :param possible: potential neighbors [with related data]
        :param parameters: additional parameters
        :return: dataframe with column containing list of ids of neighbors for each who in who(s)
        """
        df = pd.DataFrame(columns=[ckey := 'N__' + column_name])
        for who in whos.itertuples():
            df = df.append(pd.Series(data=[self.Interface.iget_neighborhood(who._asdict(), possible, **parameters)], index=[ckey], name=who[0]))
        return self.check_min(ckey, df)

    def do_work(self):
        return self.get_neighborhoods(self.name, self.eval, self.train, self.parameters)


Neighborhoods.set_config()
