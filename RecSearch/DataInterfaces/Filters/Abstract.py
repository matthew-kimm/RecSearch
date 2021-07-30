from abc import ABC, abstractmethod
import pandas as pd
from RecSearch.DataInterfaces.Shared.Config import InterfaceConfig
from functools import cache


class SharedFilter(InterfaceConfig):
    # Need Some Kind of Cleanup After Job, cache stays in memory
    @cache
    def load_csv_cached(self, file_location, idx_column):
        return pd.read_csv(file_location, index_col=idx_column)

    def clean_up(self):
        self.load_csv_cached.cache_clear()


class IFilterFromFile(ABC, SharedFilter):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'filter_file'): {'doc': super().get_doc(key),
                                                                   'input': 'file()',
                                                                   'validate': 'string()'}
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_filter(self, who: dict, possible: pd.DataFrame, filter_file: str) -> list:
        """
        Abstract method to be implemented for getting filter of an id based on data.
        :param who: dict containing index (id) with related data to find neighborhood using the possible dataframe
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param filter_file: rules for filtering (prerequisites)
        :return: list containing ids of neighbors (namedtuples so can store additional info about neighbor relation)
                                                    e.g. [Neighbor(id=9705551234, similarity=0.8), ...]
        """
        pass


IFilterFromFile.set_config()


class IFilterFromFileParameter(ABC, SharedFilter):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'history_col'): {'doc': super().get_doc(key),
                                                                  'input': 'column()',
                                                                  'validate': 'string()'
                                                                  },
                                          (key := 'filter_file'): {'doc': super().get_doc(key),
                                                                   'input': 'file()',
                                                                   'validate': 'string()'},
                                          (key := 'passing_grade'): {'doc': super().get_doc(key),
                                                                     'input': 'text()',
                                                                     'validate': 'float()'}
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_filter(self, who: dict, possible: pd.DataFrame, history_col: str, filter_file: str, passing_grade: float) -> list:
        """
        Abstract method to be implemented for getting filter of an id based on data.
        :param who: dict containing index (id) with related data to find neighborhood using the possible dataframe
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param history_col: item history column
        :param filter_file: rules for filtering (prerequisites)
        :param passing_grade: grade to count item in history as completed for prerequisite purposes.
        :return: list containing ids of neighbors (namedtuples so can store additional info about neighbor relation)
                                                    e.g. [Neighbor(id=9705551234, similarity=0.8), ...]
        """
        pass


IFilterFromFileParameter.set_config()
