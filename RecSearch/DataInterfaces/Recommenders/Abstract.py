from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from RecSearch.DataInterfaces.Shared.Config import InterfaceConfig


class SharedRecommenders(InterfaceConfig):
    def neighbor_filter(self, neighbors: list, possible: pd.DataFrame):
        """Used for filtering neighbors"""
        indices = [n['Index'] for n in neighbors]
        return possible[possible.index.isin(indices)]

    def get_reduced_df(self, who: dict, possible: pd.DataFrame, n_column: str):
        neighbors = who['N__' + n_column]
        return self.neighbor_filter(neighbors, possible)

    def neighbor_attr(self, who: dict, n_column: str):
        neighbors = who['N__' + n_column]
        return pd.DataFrame(neighbors).set_index('Index')

    def get_filter(self, who: dict, filter_name: str):
        if filter_name is None:
            return []
        else:
            return who['F__' + filter_name]


class SharedMatrixRecommenders(SharedRecommenders):
    def createAdjacencyMatrix(self, df: pd.DataFrame, columns: list, values: list):
        return df.pivot(columns=columns, values=values).fillna(0)

    def createBipartiteHITSMatrix(self, A: pd.DataFrame):
        return A.T@A

    def addTeleportation(self, B: pd.DataFrame, xi: float):
        if (xi > 0) and (xi < 1):
            return xi * B + (1-xi) * np.ones(B.shape) / B.shape[0]
        else:
            raise NotImplementedError

    def powerIteration(self, M: pd.DataFrame, tol: float, max_iter: int, names: list):
        n = M.shape[0]
        v = np.random.rand(n, 1)
        v = v / np.linalg.norm(v, 1)
        for i in range(0, max_iter):
            nv = M@v
            nv = nv / np.linalg.norm(nv, 1)
            if np.linalg.norm(v-nv, 1) < tol:
                v = nv
                break
            v = nv
        return pd.Series(data=v.values.reshape(n), index=names)

    def sortedResult(self, v: pd.Series):
        return list(v.sort_values(ascending=False).index)


class IDummyRecommender(ABC, SharedRecommenders):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'ir_column'): {'doc': super().get_doc(key),
                                                                 'input': 'column()',
                                                                 'validate': 'string()'
                                                                 }
                                          },
                             'optional': {(key := 'filter_name'): {'doc': super().get_doc(key),
                                                                   'input': 'filters()',
                                                                   'validate': 'string(default=None)'
                                                                   }

                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, ir_column: str,
                            filter_name: str = None) -> list:
        """
        Abstract method to be implemented for getting recommendation for an id based on data.
        :param who: namedtuple containing index (id) with related data for recommendation from possible
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param ir_column: item rating column {item1: rating, item2: rating, ...} (in possible df)
        :return: list containing recommended items
        """
        pass


IDummyRecommender.set_config()


class IDummyRecommenderHistory(ABC, InterfaceConfig):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'ir_column'): {'doc': super().get_doc(key),
                                                                 'input': 'column()',
                                                                 'validate': 'string()'
                                                                 },
                                          (key := 'history_col'): {
                                                                 'doc': super().get_doc(key),
                                                                 'input': 'column()',
                                                                 'validate': 'string()'
                                                                      }
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, ir_column: str, history_col: str) -> list:
        """
        Abstract method to be implemented for getting recommendation for an id based on data.
        :param who: namedtuple containing index (id) with related data for recommendation from possible
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param ir_column: item rating column {item1: rating, item2: rating, ...} (in possible df)
        :param history_col: item rating history
        :return: list containing recommended items
        """
        pass


IDummyRecommenderHistory.set_config()


class IDummyRecommender1Parameter(ABC, InterfaceConfig):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'ir_column'): {'doc': super().get_doc(key),
                                                                 'input': 'column()',
                                                                 'validate': 'string()'
                                                                 },
                                          (key := 'perfect_rating'): {
                                                                 'doc': super().get_doc(key),
                                                                 'input': 'text()',
                                                                 'validate': 'float()'
                                                                      }
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, ir_column: str, perfect_rating: float) -> list:
        """
        Abstract method to be implemented for getting recommendation for an id based on data.
        :param who: namedtuple containing index (id) with related data for recommendation from possible
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param ir_column: item rating column {item1: rating, item2: rating, ...} (in possible df)
        :param perfect_rating: what is a good rating value for a perfect recommender
        :return: list containing recommended items
        """
        pass


IDummyRecommender1Parameter.set_config()


class IRecommender(ABC, SharedRecommenders):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'n_column'): {'doc': super().get_doc(key),
                                                                'input': 'neighborhood()',
                                                                'validate': 'string()'
                                                                },
                                          (key := 'ir_column'): {'doc': super().get_doc(key),
                                                                 'input': 'column()',
                                                                 'validate': 'string()'
                                                                 }
                                          },
                             'optional': {(key := 'filter_name'): {'doc': super().get_doc(key),
                                                                   'input': 'filters()',
                                                                   'validate': 'string(default=None)'
                                                                   }
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, n_column: str, ir_column: str, filter_name: str = None) -> list:
        """
        Abstract method to be implemented for getting recommendation for an id based on data.
        :param who: namedtuple containing index (id) with related data for recommendation from possible
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param n_column: neighbors column (in who tuple)
        :param ir_column: item rating column {item1: rating, item2: rating, ...} (in possible df)
        :param filter_name: name of filter for filtering items
        :return: list containing recommended items
        """
        pass


IRecommender.set_config()


class ICountRecommender(ABC, SharedRecommenders):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'n_column'): {'doc': super().get_doc(key),
                                                                'input': 'neighborhood()',
                                                                'validate': 'string()'
                                                                },
                                          (key := 'ir_column'): {'doc': super().get_doc(key),
                                                                 'input': 'column()',
                                                                 'validate': 'string()'
                                                                 },
                                          (key := 'count'): {'doc': super().get_doc(key),
                                                             'input': 'text()',
                                                             'validate': 'integer(min=0)'}
                                          },
                             'optional': {(key := 'filter_name'): {'doc': super().get_doc(key),
                                                                   'input': 'filters()',
                                                                   'validate': 'string(default=None)'
                                                                   }
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, n_column: str, ir_column: str, count: int, filter_name: str = None) -> list:
        """
        Abstract method to be implemented for getting recommendation for an id based on data.
        :param who: namedtuple containing index (id) with related data for recommendation from possible
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param n_column: neighbors column (in who tuple)
        :param ir_column: item rating column {item1: rating, item2: rating, ...} (in possible df)
        :param count: required count
        :param filter_name: name of filter for filtering items
        :return: list containing recommended items
        """
        pass


ICountRecommender.set_config()


class IMatrixRecommender(ABC, SharedMatrixRecommenders):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'n_column'): {'doc': super().get_doc(key),
                                                                'input': 'neighborhood()',
                                                                'validate': 'string()'
                                                                },
                                          (key := 'ir_column'): {'doc': super().get_doc(key),
                                                                 'input': 'column()',
                                                                 'validate': 'string()'},
                                          (key := 'req_rating'): {'doc': super().get_doc(key),
                                                                  'input': 'text()',
                                                                  'validate': 'float()'},
                                          (key := 'xi'): {'doc': super().get_doc(key),
                                                          'input': 'text()',
                                                          'validate': 'float(min=0.0001, max=0.9999)'},
                                          (key := 'tol'): {'doc': super().get_doc(key),
                                                           'input': 'text()',
                                                           'validate': 'float()'},
                                          (key := 'max_iter'): {'doc': super().get_doc(key),
                                                                'input': 'text()',
                                                                'validate': 'integer()'}
                                          },
                             'optional': {(key := 'filter_name'): {'doc': super().get_doc(key),
                                                                   'input': 'filters()',
                                                                   'validate': 'string(default=None)'
                                                                   }
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, n_column: str, ir_column: str,
                            req_rating: float, xi: float, tol: float, max_iter: int, filter_name: str = None) -> list:
        """
        Abstract method to be implemented for getting recommendation for an id based on data.
        :param who: namedtuple containing index (id) with related data for recommendation from possible
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param n_column: neighbors column (in who tuple)
        :param ir_column: item rating column {item1: rating, item2: rating, ...} (in possible df)
        :param req_rating: the rating required to form a link in the matrix
        :param xi:  0 < xi < 1 controls how often to use matrix transition over teleportation
        :param tol: tolerance for convergence
        :param max_iter: maximum iterations to run for
        :param filter_name: name of filter for filtering items
        :return: list containing recommended items
        """
        pass


IMatrixRecommender.set_config()


class IMatrixNeighborRecommender(ABC, SharedMatrixRecommenders):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'n_column'): {'doc': super().get_doc(key),
                                                                'input': 'neighborhood()',
                                                                'validate': 'string()'},
                                          (key := 'ir_column'): {'doc': super().get_doc(key),
                                                                 'input': 'column()',
                                                                 'validate': 'string()'},
                                          (key := 'xi'): {'doc': super().get_doc(key),
                                                          'input': 'text()',
                                                          'validate': 'float(min=0.0001, max=0.9999)'},
                                          (key := 'tol'): {'doc': super().get_doc(key),
                                                           'input': 'text()',
                                                           'validate': 'float(default=10e-6)'},
                                          (key := 'max_iter'): {'doc': super().get_doc(key),
                                                                'input': 'text()',
                                                                'validate': 'integer()'}
                                          },
                             'optional': {(key := 'filter_name'): {'doc': super().get_doc(key),
                                                                   'input': 'filters()',
                                                                   'validate': 'string(default=None)'
                                                                   }
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, n_column: str, ir_column: str,
                            xi: float, tol: float, max_iter: int, filter_name: str = None) -> list:
        """
        Abstract method to be implemented for getting recommendation for an id based on data.
        :param who: namedtuple containing index (id) with related data for recommendation from possible
        :param possible: dataframe containing id and related data of possible neighbors of who.
        :param n_column: neighbors column (in who tuple)
        :param ir_column: item rating column {item1: rating, item2: rating, ...} (in possible df)
        :param xi: 0 < xi < 1 controls how often to use matrix transition over teleportation
        :param tol: tolerance for convergence
        :param max_iter: maximum iterations to run for
        :param filter_name: name of filter for filtering items
        :return: list containing recommended items
        """
        pass


IMatrixNeighborRecommender.set_config()
