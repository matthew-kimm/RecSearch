from abc import ABC, abstractmethod
import pandas as pd
from RecSearch.DataInterfaces.Shared.Config import InterfaceConfig


class SharedSplitter(InterfaceConfig):
    pass


class ISplitter(ABC, InterfaceConfig):
    """
    Interface te split data into sets; e.g. Train, Validate, Test.
    """
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'train'): {'doc': super().get_doc(key),
                                                           'input': 'text()',
                                                           'validate': 'float(min=0.001, max=0.999, default=0.8)'
                                                            },
                                          (key := 'test'): {'doc': super().get_doc(key),
                                                            'input': 'text()',
                                                            'validate': 'float(min=0.001, max=0.999, default=0.2)'},
                                          },
                             'optional': {(key := 'validate'): {'doc': super().get_doc(key),
                                                                'input': 'text(disabled=True)',
                                                                'validate': 'float(min=0.001,max=0.999, default=None)'}
                                          }

                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    @abstractmethod
    def iget_splitter(self, data: pd.DataFrame, train: float, test: float, validate: float = None) -> dict:
        """
        Abstract method to be implemented splits data into sets for train, validate, test paradigm.
        :param data: data to be split
        :param train: how to split train data
        :param test: how to split test data
        :param validate: how to split validate data (optional)
        :return: dict of pd.DataFrame
        """


ISplitter.set_config()
