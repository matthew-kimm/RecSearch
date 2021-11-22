from abc import ABC, abstractmethod
import pandas as pd
from RecSearch.DataInterfaces.Shared.Config import InterfaceConfig


class SharedNeighborhood(InterfaceConfig):
    def to_dicts(self, iterable):
        """Convert itertuples() iterable of namedtuples to list of dicts"""
        return [item._asdict() for item in iterable]

    def neighbor_filter(self, neighbors: list, df: pd.DataFrame):
        """Used for filtering neighbors when chaining interfaces"""
        indices = [n['Index'] for n in neighbors]
        return df[df.index.isin(indices)]


class INeighborhood(ABC, SharedNeighborhood):
    @abstractmethod
    def iget_neighborhood(self, who: dict, possible: pd.DataFrame) -> list:
        """
        Abstract method to be implemented for getting neighborhood of an id based on data.
        :param who: dict containing index (id) with related data to find neighborhood using the possible dataframe
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :return: list containing ids of neighbors (namedtuples so can store additional info about neighbor relation)
                                                    e.g. [Neighbor(id=101, similarity=0.8), ...]
        """
        pass


class INeighborhoodAttributes(ABC, SharedNeighborhood):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'attributes'): {'doc': super().get_doc(key),
                                                                  'input': 'columns()',
                                                                  'validate': 'string_list()'
                                                                  }
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_neighborhood(self, who: dict, possible: pd.DataFrame, attributes: list) -> list:
        """
        Abstract method to be implemented for getting neighborhood of an id based on data.
        :param who: dict containing index (id) with related data to find neighborhood using the possible dataframe
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param attributes: list of attributes to match
        :return: list containing ids of neighbors (namedtuples so can store additional info about neighbor relation)
                                                    e.g. [Neighbor(id=101, similarity=0.8), ...]
        """


INeighborhoodAttributes.set_config()


class INeighborhoodGradeAttributes(ABC, SharedNeighborhood):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'attributes'): {'doc': super().get_doc(key),
                                                                  'input': 'columns()',
                                                                  'validate': 'string_list()'
                                                                   },
                                          (key := 'item_history_col'): {'doc': super().get_doc(key),
                                                                        'input': 'column()',
                                                                        'validate': 'string()'},
                                          (key := 'exact_grade'): {'doc': super().get_doc(key),
                                                                   'input': 'checkbox()',
                                                                   'validate': 'boolean()'}
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_neighborhood(self, who: dict, possible: pd.DataFrame, attributes: list,
                          item_history_col: str, exact_grade: bool) -> list:
        """
        Abstract method to be implemented for getting neighborhood of an id based on data.
        :param who: dict containing index (id) with related data to find neighborhood using the possible dataframe
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param attributes: list of attributes to match
        :param item_history_col: column containing dict of form {item: rating}
        :param exact_grade: Match on the exact grade. (False numerically matches only letter of grade
        using the 4.0, 3.7, 3.3, 3.0, ... scale)
        :return: list containing ids of neighbors (namedtuples so can store additional info about neighbor relation)
                                                    e.g. [Neighbor(id=101, similarity=0.8), ...]
        """


INeighborhoodGradeAttributes.set_config()


class INeighborhoodGrade(ABC, SharedNeighborhood):
    @classmethod
    def set_config(cls):
        additional_config = {'required':  {(key := 'item_history_col'): {'doc': super().get_doc(key),
                                                                         'input': 'column()',
                                                                         'validate': 'string()'},
                                           (key := 'exact_grade'): {'doc': super().get_doc(key),
                                                                    'input': 'checkbox()',
                                                                    'validate': 'boolean()'}

                                           }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_neighborhood(self, who: dict, possible: pd.DataFrame, item_history_col: str, exact_grade: bool) -> list:
        """
        Abstract method to be implemented for getting neighborhood of an id based on data.
        :param who: dict containing index (id) with related data to find neighborhood using the possible dataframe
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param item_history_col: column containing dict of form {item: rating}
        :param exact_grade: Match on the exact grade. (False numerically matches only letter of grade
        using the 4.0, 3.7, 3.3, 3.0, ... scale)
        :return: list containing ids of neighbors (namedtuples so can store additional info about neighbor relation)
                                                    e.g. [Neighbor(id=101, similarity=0.8), ...]
        """


INeighborhoodGrade.set_config()
