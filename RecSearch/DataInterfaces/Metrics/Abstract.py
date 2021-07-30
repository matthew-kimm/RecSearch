from abc import ABC, abstractmethod
from RecSearch.DataInterfaces.Shared.Config import InterfaceConfig

#TODO: Fix metrics to use list of recommender columns or * rather than single

class MetricShared(InterfaceConfig):
    pass

class IMetric(ABC, MetricShared):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'rec_column'):
                                              {'doc': super().get_doc(key),
                                               'input': 'recommender()',
                                               # Change to custom type to match list or *
                                               'validate': 'string_list()'
                                               },
                                          (key := 'ir_column'):
                                              {'doc': super().get_doc(key),
                                               'input': 'column()',
                                               'validate': 'string()'}
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_metric(self, who: dict, rec_column: str, ir_column: str) -> dict:
        """
        Abstract method to be implemented for computing metric of rec_column given item-rating column
        :param who: a dict representing a user with at least Index, Recommendation, Item-Rating
        :param rec_column: list recommendation column name or *
        :param ir_column: item-rating column name
        :return:
        """


IMetric.set_config()


class IMetricBaselineHistory(ABC, MetricShared):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'rec_column'):
                                              {'doc': super().get_doc(key),
                                               'input': 'recommender()',
                                               # Change to custom type to match list or *
                                               'validate': 'string_list()'
                                               },
                                          (key := 'ir_column'):
                                              {'doc': super().get_doc(key),
                                               'input': 'column()',
                                               'validate': 'string()'},
                                          (key := 'history_column'):
                                              {'doc': super().get_doc(key),
                                               'input': 'column()',
                                               'validate': 'string()'}
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_metric(self, who: dict, rec_column: str, ir_column: str, history_column) -> dict:
        """
        Abstract method to be implemented for computing metric of rec_column given item-rating column
        :param who: a dict representing a user with at least Index, Recommendation, Item-Rating
        :param rec_column: list recommendation column name or *
        :param ir_column: item-rating column name
        :param history_column: item-rating history column name
        :return:
        """


IMetricBaselineHistory.set_config()


class IMetricThreshold(ABC, MetricShared):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'rec_column'):
                                              {'doc': super().get_doc(key),
                                               'input': 'recommender()',
                                               # Change to custom type to match list or *
                                               'validate': 'string_list()'
                                               },
                                          (key := 'ir_column'):
                                              {'doc': super().get_doc(key),
                                               'input': 'column()',
                                               'validate': 'string()'},
                                          (key := 'threshold'):
                                              {'doc': super().get_doc(key),
                                               'input': 'text()',
                                               'validate': 'float(min=0.0, max=4.0, default=2.0)'}
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_metric(self, who: dict, rec_column: str, ir_column: str, threshold: str) -> dict:
        """
        Abstract method to be implemented for computing metric of rec_column given item-rating column
        :param who: a dict representing a user with at least Index, Recommendation, Item-Rating
        :param rec_column: list recommendation column name or *
        :param ir_column: item-rating column name
        :param threshold: threshold to count course as meeting metric
        :return:
        """


IMetricThreshold.set_config()
