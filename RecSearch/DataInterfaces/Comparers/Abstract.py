from abc import ABC, abstractmethod
from RecSearch.DataInterfaces.Shared.Config import InterfaceConfig

#TODO: Fix metrics to use list of recommender columns or * rather than single

class ComparerShared(InterfaceConfig):
    pass

class IComparer(ABC, ComparerShared):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'metric'):
                                              {'doc': super().get_doc(key),
                                               'input': 'metric()',
                                               # Change to custom type to match list or *
                                               'validate': 'string()'
                                               },
                                          (key := 'compare_to'):
                                              {'doc': super().get_doc(key),
                                               'input': 'metric_recommender()',
                                               'validate': 'string()'}
                                          },
                             'optional': {(key := 'length'):
                                              {'doc': super().get_doc(key),
                                               'input': 'text()',
                                               'validate': 'integer(min=0, default=None)'}}
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_comparer(self, who: dict, metric: str, compare_to: str, length: int = None) -> dict:
        """
        Abstract method to be implemented for computing comparison of recommenders in metric to compare to.
        :param who: a dict representing a user with at least Index, Recommendation, Item-Rating
        :param rec_column: list recommendation column name or *
        :param ir_column: item-rating column name
        :return:
        """


IComparer.set_config()
