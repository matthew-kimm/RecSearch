from RecSearch.Config.ConfigValidator import default_validator
from RecSearch.Config.ConfigGenMeta import meta_data_objects
from RecSearch.Config.ConfigGenKeyManage import default_key_manager


class InputValidator:
    """Validates input using ConfigObj Validator"""
    def __init__(self):
        self.meta_dw, self.meta_di = meta_data_objects()
        self.key_manager = default_key_manager
        self.validator = default_validator

    def get_default(self, param_key: str):
        """
        Get the default value of a parameter from check string
        :param param_key: GUI key
        :return:
        """
        if ':Interface:' in param_key:
            __, ptype, dw, method, var = param_key.split(':')[1:]
            try:
                return self.validator.get_default_value(self.meta_di.get_check(dw, method, var, ptype))
            except:
                return None
        else:
            __, ptype, dw, var = param_key.split(':')[1:]
            try:
                return self.validator.get_default_value(self.meta_dw.get_check(dw, var, ptype))
            except:
                return None

    def optional_fix(self, value):
        if value:
            return value
        else:
            return None

    def individual_check(self, check_key: str, gui_values: dict):
        """
        Check an individual parameter using check string in class config
        :param check_key: GUI parameter check key
        :param gui_values: GUI value for parameter
        :return:
        """
        gui_key = ':'.join(check_key.split(':')[:-1])
        if ':Optional' in check_key:
            check_value = self.optional_fix(gui_values[gui_key])
        else:
            check_value = gui_values[gui_key]
        if ':Interface:' in check_key:
            __, ptype, dw, method, var, __ = check_key.split(':')[1:]
            try:
                # validator.check returns converted value taking bool works except for int/float = 0 when checking req
                # When checking optional, we have default=None in the check
                return (bool(self.validator.check(self.meta_di.get_check(dw, method, var, ptype), check_value)) or
                        self.validator.check(self.meta_di.get_check(dw, method, var, ptype), check_value) is None or
                        self.validator.check(self.meta_di.get_check(dw, method, var, ptype), check_value) == 0)
            except:
                # Catch all Validator Errors
                return False
        else:
            __, ptype, dw, var, __ = check_key.split(':')[1:]
            try:
                return (bool(self.validator.check(self.meta_dw.get_check(dw, var, ptype), check_value)) or
                        self.validator.check(self.meta_dw.get_check(dw, var, ptype), check_value) is None or
                        self.validator.check(self.meta_dw.get_check(dw, var, ptype), check_value) == 0)
            except:
                # Catch all Validator Errors
                return False

    def check_all_worker(self, data_worker: str, gui_values: dict):
        """
        Check all parameters relating to dataworker and interface
        :param data_worker: Name of DataWorker
        :param gui_values: GUI values dict produced after event
        :return:
        """
        key_manage = getattr(self.key_manager, data_worker)
        worker_check_base = all([self.individual_check(key, gui_values)
                                 for key in key_manage.get_worker_check_keys(data_worker)])
        method_key = key_manage.get_method_key(data_worker)
        method = gui_values[method_key]
        worker_check_interface = all(self.individual_check(key, gui_values) for key in key_manage.get_method_check_keys(method))
        return worker_check_base and worker_check_interface
