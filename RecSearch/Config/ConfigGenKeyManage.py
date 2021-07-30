"""Keys Identify GUI Elements for Control"""
from RecSearch.Config.ConfigGenMeta import meta_data_objects


class DataWorkerKeyManager:
    """Main Key Manager for all dataworkers"""
    def __init__(self):
        self.meta_dw, __ = meta_data_objects()
        for name in self.meta_dw.get_dataworkers():
            setattr(self, name, KeyManager(name))

    def get_update_keys(self, update_type: str) -> list:
        """
        Get keys (from every dataworker) for updating options from program state
         e.g. Includes keys needed to update neighborhoods for choosing when configuring recommender interface.
        :param update_type: prefix for update keys (defined in InputDef functions)
        :return: list of GUI keys
        """
        update_keys = []
        for name in self.meta_dw.get_dataworkers():
            update_keys += getattr(self, name).get_update_keys(update_type)
        return update_keys


class KeyManager:
    """KeyManager for individual dataworker"""
    def __init__(self, data_worker: str):
        """
        :param data_worker: DataWorker name (matches some /RecSearch/DataWorkers/.)
        """
        self.dw = data_worker
        self.dw_main_keys = set()
        self.dw_param_keys = set()
        self.dw_update_types = set()

    def get_update_keys(self, update_type: str) -> list:
        """
        Get keys for updating options from program state of this keymanager (specific dataworker)
        :param update_type: prefix for update keys (defined in InputDef functions)
        :return: list of GUI keys
        """
        update_keys = [key for key in self.dw_main_keys | self.dw_param_keys if key.startswith(update_type)]
        return update_keys

    def get_method_key(self, worker: str) -> str:
        """
        Get key for choosing DataInterface for the DataWorker.
        :param worker:  DataWorker name (matches some /RecSearch/DataWorkers/.)
        :return:
        """
        req_keys = self.get_worker_keys(worker)
        method_key, = [key for key in req_keys if key.endswith(':method')]
        return method_key

    def get_param_key_worker(self, worker: str, param: str) -> str:
        """
        Get key for a specific parameter related to DataWorker (but not its interface's parameters)
        :param worker: DataWorker name (matches some /RecSearch/DataWorkers/.)
        :param param: Parameter associated with the DataWorker.
        :return: GUI key
        """
        param_key, = [key for key in self.dw_param_keys
                      if (':Worker:' in key)
                      and (self.make_sub_key(worker) in key)
                      and key.endswith(':' + param)]
        return param_key

    def get_param_key_interface(self, worker: str, interface: str, param: str) -> str:
        """
        Get key for a specific parameter related to DataWorker Interface
        :param worker: DataWorker name (matches some /RecSearch/DataWorkers/.)
        :param interface: Interface name (matches some /RecSearch/DataInterfaces/[worker]/.)
        :param param: Parameter associated with the DataWorker.
        :return: GUI key
        """
        param_key, = [key for key in self.dw_param_keys
                      if (':Interface:' in key)
                      and (self.make_sub_key(worker) in key)
                      and (self.make_sub_key(interface) in key)
                      and key.endswith(':' + param)]
        return param_key

    def get_all_worker_keys(self, worker: str) -> list:
        """
        Get GUI keys for required and optional DataWorker parameters.
        :param worker:
        :return:
        """
        req_and_opt_worker_keys = self.get_worker_keys(worker, required=True) +\
                                  self.get_worker_keys(worker, required=False)
        return req_and_opt_worker_keys

    def get_all_interface_keys(self, worker: str, interface: str) -> list:
        """
        Get GUI keys for required and optional Dataworker's Interface parameters.
        :param worker:
        :param interface:
        :return:
        """
        if not interface:
            req_and_opt_interface_keys = []
        else:
            req_and_opt_interface_keys = self.get_interface_keys(worker, interface, required=True) +\
                                         self.get_interface_keys(worker, interface, required=False)
        return req_and_opt_interface_keys

    def get_worker_keys(self, worker: str, required: bool = True) -> list:
        """
        Get all GUI keys for (required or optional) DataWorker parameters
        :param worker: DataWorker name (matches some /RecSearch/DataWorkers/.)
        :param required: True gets required, False gets optional
        :return: list of GUI keys
        """
        req_or_opt_worker_keys = [key for key in self.dw_param_keys
                                  if (':Worker:' in key)
                                  and (self.make_sub_key(worker) in key)
                                  and (':Required:' in key if required else ':Optional:' in key)
                                  and (not (key.endswith(':Check') or key.endswith(':Help')))]
        return req_or_opt_worker_keys

    def get_interface_keys(self, worker: str, interface: str, required: bool = True) -> list:
        """
        Get all GUI keys for (required or optional) DataWorker's Interface parameters.
        :param worker: DataWorker name (matches some /RecSearch/DataWorkers/.)
        :param interface: Interface name (matches some /RecSearch/DataInterfaces/[worker]/.)
        :param required: True gets required, False gets optional
        :return: list of GUI keys
        """
        req_or_opt_interface_keys = [key for key in self.dw_param_keys
                                     if (':Interface:' in key)
                                     and (self.make_sub_key(worker) in key)
                                     and (interface in key)
                                     and (':Required:' in key if required else 'Optional' in key)
                                     and (not (key.endswith(':Check') or key.endswith(':Help')))]
        return req_or_opt_interface_keys

    def make_sub_key(self, key: str) -> str:
        """
        Convert string to subpart of key
        :param key: string to format as :string:
        :return:
        """
        sub_key = ':' + key + ':'
        return sub_key

    def get_method_keys(self, method: str) -> list:
        """Get GUI keys for DataWorker's Interface parameters (including related check/help button)"""
        method_keys = [key for key in self.dw_param_keys if key.split(':')[-2] == method]
        return method_keys

    def get_method_check_keys(self, method: str) -> list:
        """Get GUI keys for DataWorker's Interface's parameters' check buttons"""
        method_check_keys = [key + ':Check' for key in self.get_method_keys(method)]
        return method_check_keys

    def get_update_param_keys(self, update_type: str) -> list:
        """
        Doesn't seem to be used
        Get GUI keys for an update type (update options to current state of program)
        :param update_type: Type comes from dw_update_types"""
        update_type_param_keys = [key for key in self.dw_param_keys if key.startswith(update_type)]
        return update_type_param_keys

    def get_worker_check_keys(self, worker: str) -> list:
        """Get GUI keys for DataWorker's parameters' check buttons"""
        worker_with_interface_check_keys = [key for key in self.dw_param_keys
                                            if (':Worker:' in key)
                                            and (self.make_sub_key(worker) in key)
                                            and (key.endswith(':Check'))]
        return worker_with_interface_check_keys

    def update_main_keys(self, keys: list) -> None:
        """Add keys to the main keys that control viewing and state for the DataWorker"""
        self.dw_main_keys.update(keys)

    def update_param_keys(self, keys: list) -> None:
        """Add keys to the parameter keys for the DataWorker (its parameters and its interface's parameters)"""
        self.dw_param_keys.update(keys)

    def get_dw_req_base(self) -> str:
        """Get base key for a required parameter of a DataWorker (not its interface)"""
        return ':Worker:Required:' + self.dw

    def get_dw_opt_base(self) -> str:
        """Get base key for an optional parameter of a DataWorker (not its interface)"""
        return ':Worker:Optional:' + self.dw

    def get_di_req_base(self, di_name: str) -> str:
        """Get base key for a required parameter of a DataWorker's interface"""
        return ':Interface:Required:' + self.dw + ':' + di_name

    def get_di_opt_base(self, di_name: str) -> str:
        """Get base key for an optional parameter of a DataWorker's interface"""
        return ':Interface:Optional:' + self.dw + ':' + di_name

    def update_types(self, keys) -> None:
        """Add keys to the keys for updating options based on program state"""
        self.dw_update_types.update(keys)


# Global key manager for the ConfigGenerator
default_key_manager = DataWorkerKeyManager()
