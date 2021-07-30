"""
Finds DataWorkers/DataInterfaces from file directory structure
 and stores the configurations (see ./ConfigManagement.py for a description)
 in a central location.
"""
import glob
import importlib
from string import ascii_lowercase, ascii_uppercase
from RecSearch.DataInterfaces.Factory import InterfaceFactory
from RecSearch.Config.ConfigValidator import default_validator
from os import sep as os_sep
from typing import Tuple
from os import getcwd


class MetaDataInterfaces:
    """
    Information on DataInterfaces.

    DataInterfaces should be stored as RecSearch/DataInterfaces/(Parent DataWorker)/name_of_data_interface.py

    name_of_data_interface must start with ascii lowercase.

    Also, Non-DataInterfaces (maybe shared resources) in this folder must not start with ascii lowercase.
    """
    def __init__(self):
        self.data_interface_objects = self.get_objects()
        self.di_parameter_configs = self.get_parameter_configs()

    def get_all_checks(self, dw: str, di: str) -> dict:
        """Get the check strings (for ConfigObj) from class cfg for each Data Interface"""
        di_checks = {}
        req = self.get_required(dw, di)
        for key in req.keys():
            di_checks[key] = req[key]['validate']
        opt = self.get_optional(dw, di)
        for key in opt.keys():
            di_checks[key] = opt[key]['validate']
        return di_checks

    def get_help(self, folder: str, name: str, param: str, required: str) -> str:
        """
        Get the doc string for DataInterface parameter from this
        :param folder: Name of Parent DataWorker
        :param name: Name of DataInterface
        :param param: Name of Parameter
        :param required: 'Required' or 'Optional'
        :return:
        """
        if required == 'Required':
            help_string = self.get_required(folder, name)[param].get('doc', 'No Documentation')
        else:
            help_string = self.get_optional(folder, name)[param].get('doc', 'No Documentation')
        return help_string

    def get_check(self, folder: str, name: str, param: str, required: str) -> str:
        """
        Get the check string for DataInterface parameter from this
        :param folder: Name of Parent DataWorker
        :param name: Name of DataInterface
        :param param: Name of Parameter
        :param required: 'Required' or 'Optional'
        :return:
        """
        if required == 'Required':
            check_string = self.get_required(folder, name)[param].get('validate', 'pass')
        else:
            check_string = self.get_optional(folder, name)[param].get('validate', 'pass')
        return check_string

    def get_required(self, folder, name) -> dict:
        """
        Get DataInterface required parameters
        :param folder: Name of Parent DataWorker
        :param name: Name of DataInterface
        :return:
        """
        di_required_param = self.di_parameter_configs[folder][name]['required']
        return di_required_param

    def get_optional(self, folder, name) -> dict:
        """
        Get DataInterface optional parameters
        :param folder: Name of parent DataWorker
        :param name: Name of DataInterface
        :return:
        """
        di_optional_param = self.di_parameter_configs[folder][name]['optional']
        return di_optional_param

    def get_interfaces(self, folder) -> list:
        """
        Get DataInterfaces for a parent DataWorker from this
        :param folder: Name of parent DataWorker
        :return:
        """
        if folder in self.data_interface_objects.keys():
            data_interfaces = list(self.data_interface_objects[folder].keys())
        else:
            data_interfaces = []
        return data_interfaces

    def get_objects(self) -> dict:
        """Use Directory/Class/Object structure to get DataInterface Objects"""
        # Path depends on which file is running / Running ConfigGenerator.py imports GetProgramLocation.py for this
        data_interface_all_paths = glob.glob(getcwd() + os_sep + 'DataInterfaces' + os_sep + '**' + os_sep + '*.py')
        # (Interface Folder, Interface File Name)
        data_interface_paths = [(mod.split(os_sep)[-2], mod.split(os_sep)[-1].removesuffix('.py'))
                                for mod in data_interface_all_paths
                                if mod.split(os_sep)[-1][0] in ascii_lowercase]
        # {folder: {name: module}}
        data_interface_objects = {}
        for folder, name in data_interface_paths:
            if folder not in data_interface_objects.keys():
                data_interface_objects[folder] = {}
            data_interface_objects[folder].update({name: InterfaceFactory.get_interface(folder, name)})
        return data_interface_objects

    def get_parameter_configs(self) -> dict:
        """Get the cfg dict for each DataInterface object from this"""
        param_dict = {}
        for folder in self.data_interface_objects.keys():
            param_dict[folder] = {}
            for name, obj in self.data_interface_objects[folder].items():
                param_dict[folder][name] = getattr(obj, 'cfg')
        return param_dict


class MetaDataWorkers:
    """Information on DataWorkers.

    DataWorkers should be stored as RecSearch/DataWorkers/Name_of_data_worker.py

    Any non-DataWorkers in this folder must be added to file_excludes below.
    """
    def __init__(self):
        # Exclude Non-DataWorker Files
        self.file_excludes = ['Abstract.py', 'Factory.py', 'Shared.py']
        self.data_worker_classes = self.get_classes()
        self.dw_parameter_configs = self.get_parameter_configs()
        self.validator = default_validator

    def get_any_check(self, dw: str, var: str) -> str:
        """Get check string for DataWorker parameter"""
        req = self.get_check(dw, var, 'Required')
        opt = self.get_check(dw, var, 'Optional')
        if req != 'pass':
            return req
        elif opt != 'pass':
            return opt
        else:
            print('Warning: Check not found or is the pass check')
            return 'pass'

    def get_precedence(self, dw: str) -> int:
        """Get precedence of DataWorker"""
        return self.validator.get_default_value(self.get_required(dw)['precedence']['validate'])

    def get_all_checks(self, dw: str) -> dict:
        """Get all check strings for a DataWorker"""
        dw_checks = {}
        req = self.get_required(dw)
        for key in req.keys():
            dw_checks[key] = req[key]['validate']
        opt = self.get_optional(dw)
        for key in opt.keys():
            # use validator_func(..., default=None) for all optional checks
            dw_checks[key] = opt[key]['validate']
        return dw_checks

    def get_help(self, dw: str, param: str, required: str) -> str:
        """
        Get docstring from class config for DataWorker parameter
        :param dw:
        :param param:
        :param required: 'Required' or 'Optional'
        :return:
        """
        if required == 'Required':
            return self.get_required(dw)[param].get('doc', 'pass')
        else:
            return self.get_optional(dw)[param].get('doc', 'pass')

    def get_check(self, dw: str, var: str, required: str) -> str:
        """Get the check string for a DataWorker parameter"""
        if required == 'Required':
            return self.get_required(dw).get(var, {'validate': 'pass'}).get('validate', 'pass')
        else:
            return self.get_optional(dw).get(var, {'validate': 'pass'}).get('validate', 'pass')

    def get_required(self, dw) -> dict:
        """Get required parameters for DataWorker"""
        return self.dw_parameter_configs[dw]['required']

    def get_optional(self, dw) -> dict:
        """Get optional parameters for DataWorker"""
        return self.dw_parameter_configs[dw]['optional']

    def get_classes(self) -> dict:
        """Use Directory/File/Class Structure to get DataWorker classes"""
        # Path depends on which file running
        data_worker_all_paths = glob.glob(getcwd() + os_sep + 'DataWorkers/*.py')
        # (Interface Folder, Interface File Name)
        data_worker_paths = [(mod.split(os_sep)[-2], mod.split(os_sep)[-1][:-3])
                             for mod in data_worker_all_paths
                             if mod.split(os_sep)[-1] not in self.file_excludes
                             and mod.split(os_sep)[-1][0] in ascii_uppercase]
        data_worker_classes = {name: getattr(importlib.import_module('.' + name, 'RecSearch.' + path), name)
                               for path, name in data_worker_paths}
        return data_worker_classes

    def get_dataworkers(self) -> list[str]:
        """Get the names of possible DataWorker classes"""
        return list(self.data_worker_classes.keys())

    def get_parameter_configs(self) -> dict:
        """Get parameters for DataWorker"""
        worker_parameter_configs = {worker: getattr(worker_class, 'cfg')
                                    for worker, worker_class in self.data_worker_classes.items()}
        return worker_parameter_configs


def meta_data_objects() -> Tuple[MetaDataWorkers, MetaDataInterfaces]:
    """Create MetaDataWorkers and MetaDataInterfaces objects"""
    return MetaDataWorkers(), MetaDataInterfaces()


#debug_data_workers, debug_data_interfaces = meta_data_objects()
#print('debug')
