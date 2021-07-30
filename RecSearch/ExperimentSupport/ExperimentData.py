import ast
import pandas as pd
from RecSearch.DataInterfaces.Factory import InterfaceFactory
from os.path import exists
from os import mkdir
from os import sep as os_sep


class ExperimentData:
    """
    ExperimentData class manages data for an experiment.
    """
    def __init__(self, experiment_file: str, data_config: dict, data_splitter_config: dict = None,
                 load_experiment: bool = False, save_experiment: bool = True):
        """
        Setup new experiment data or load old experiment data.
        :param experiment_file: file location of experiment configuration
        :param data_config: data configuration from experiment configuration
        :param data_splitter_config: (new experiment) splitter configuration from experiment configuration
        :param load_experiment: whether to load experiment from saved data
        :param save_experiment: whether to save resulting data from experiment
                                (allows for loading to continue or expand experiment)
        """
        self.data_cfg = data_config
        self.experiment_name = experiment_file.split(os_sep)[-1].removesuffix('.cfg')
        self.experiment_folder = os_sep.join(experiment_file.split(os_sep)[:-1])\
                                 + os_sep + self.experiment_name + os_sep
        self.save_experiment = save_experiment

        # Hotfix ast_literal_eval doesn't allow nan
        def backstep_ast_literal_eval(s: pd.Series) -> list:
            output = []
            know_type = None
            for value in s:
                try:
                    output.append(obj := ast.literal_eval(value))
                    if know_type is None:
                        know_type = type(obj)
                        know_type = know_type()
                except ValueError:
                    if know_type is None:
                        output.append('Unknown')
                    else:
                        output.append(know_type)
            if know_type is None:
                raise ValueError
            correct_output = [x if x != 'Unknown' else know_type for x in output]
            return correct_output

        if data_splitter_config is not None:
            self.data = pd.read_csv(self.data_cfg['datafile'], usecols=self.data_cfg['use_columns'])
            # TEMPORARY
            # self.data = self.data.dropna()
            # END
            for column in self.data_cfg['ast_columns']:
                self.data[column] = backstep_ast_literal_eval(self.data[column])
            self.data = self.data.set_index(self.data_cfg['index_columns'])

            self.splitter_cfg = data_splitter_config
            self.data_splitter = InterfaceFactory.get_interface('Splitters', self.splitter_cfg['method'])
            for data_name, dataframe in self.data_splitter.iget_splitter(self.data, **self.splitter_cfg['parameters']).items():
                setattr(self, data_name, dataframe)
            self.eval_data = 'test'
        elif load_experiment:
            # If implement multiple eval datasets, use dynamic loading with setattr()
            self.train = pd.read_csv(self.experiment_folder + 'train.csv', index_col=self.data_cfg['index_columns'])
            self.test = pd.read_csv(self.experiment_folder + 'test.csv', index_col=self.data_cfg['index_columns'])
            for column in self.data_cfg['ast_columns']:
                self.train[column] = backstep_ast_literal_eval(self.train[column])
                self.test[column] = backstep_ast_literal_eval(self.test[column])
            dw_columns = [col for col in self.test.columns if col[:3] in ['R__', 'N__', 'F__', 'M__']]
            for col in dw_columns:
                self.test[col] = self.test[col].apply(lambda x: ast.literal_eval(x))
            # Multiple eval datasets not implemented
            self.eval_data = 'test'
        else:
            raise NotImplementedError

    def reset(self, reset_columns: list):
        self.test = self.test.drop(reset_columns, axis=1)

    def get_dataset(self, data_name: str, columns: list = None) -> pd.DataFrame:
        """
        Get dataset with columns.
        :param data_name: train or test or validate
        :param columns: needed columns
        :return: dataframe with columns
        """
        if columns is None:
            return getattr(self, data_name)
        else:
            return getattr(self, data_name)[columns]

    def update_dataset(self, data_name: str, append: pd.DataFrame):
        """
        Append column to existing data
        :param data_name: train or test or validate
        :param append: data to append
        :return:
        """
        df = getattr(self, data_name)
        setattr(self, data_name, df.join(append, how='left'))

    def save_data(self):
        if self.save_experiment:
            if not exists(self.experiment_folder):
                mkdir(self.experiment_folder)
            self.train.to_csv(self.experiment_folder + 'train.csv')
            # Multiple test sets not implemented
            self.test.to_csv(self.experiment_folder + 'test.csv')

    def set_eval_data(self, set_to: str):
        # Multiple test sets or have a validate set (Not implemented yet)
        self.eval_data = set_to

    def get_eval_data(self):
        return self.eval_data
