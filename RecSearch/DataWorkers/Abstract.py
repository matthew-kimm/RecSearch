from abc import ABC, abstractmethod
import pandas as pd
from RecSearch.ExperimentSupport.ExperimentData import ExperimentData
from RecSearch.DataInterfaces.Factory import InterfaceFactory
from RecSearch.DataWorkers.Shared import DataWorkerConfig


class GeneralDataWorkers(ABC, DataWorkerConfig):
    @classmethod
    def set_config(cls):
        additional_config = {'required': {'name': {'doc': 'Give the dataworker a name for identification',
                                                   'input': 'text()',
                                                   'validate': 'valid_name(default="my_dataworker")'},
                                          'method': {'doc': 'Interface method',
                                                     'input': 'methods()',
                                                     'validate': 'string()'}}
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    def __init__(self, class_name: str, name: str, data_worker_config: dict):
        self.name = name
        self.prefix = class_name[0] + '__'
        self.dw_cfg = data_worker_config
        self.Interface = InterfaceFactory.get_interface(class_name, self.dw_cfg['method'])
        # Mandatory and optional configs for the overall dataworker, set static top_level_configs in data worker
        self.set_top_level_config()
        self.parameters = self.dw_cfg['parameters']

    def get_column_name(self):
        return self.prefix + self.name

    def set_top_level_config(self):
        for req_cfg in self.cfg['required'].keys():
            setattr(self, req_cfg, self.dw_cfg[req_cfg])
        for opt_cfg in self.cfg['optional'].keys():
            if opt_cfg in self.cfg.keys():
                setattr(self, opt_cfg, self.dw_cfg[opt_cfg])


GeneralDataWorkers.set_config()


class DataWorkers(GeneralDataWorkers):
    """
    DataWorkers class is the shared functionality for working with experiment data. (Abstract Class)
    """
    # Configs inline with [[NAME]]
    @classmethod
    def set_config(cls):
        additional_config = {'required': {'precedence': {'doc': 'Order (ascending) to run dataworkers',
                                                         'input': 'text(disabled=True)',
                                                         'validate': 'integer()'
                                                         },
                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    def __init__(self, class_name: str, name: str, data_worker_config: dict, Data: ExperimentData):
        super().__init__(class_name, name, data_worker_config)
        self.Data = Data
        self.train = None
        self.eval = None

    def request_data(self, data_name: str, columns: list = None) -> pd.DataFrame:
        return self.Data.get_dataset(data_name, columns)

    def send_data(self, data_name: str, append: pd.DataFrame):
        self.Data.update_dataset(data_name, append)

    def do_the_work(self):
        self.train = self.request_data('train')
        self.eval = self.request_data(self.Data.get_eval_data())
        new_data = self.do_work()
        self.train = None
        self.eval = None
        self.send_data(self.Data.get_eval_data(), new_data)

    @abstractmethod
    def do_work(self):
        # Dataworker does its job
        pass


DataWorkers.set_config()
