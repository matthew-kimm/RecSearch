import inspect
from copy import deepcopy
import re


class ConfigManage:
    """
    Provides methods for managing parameter configuration for all DataWorker/DataInterface classes
    (must inherit this class).
    Each parameter:
        specifies some documentation (or retrieves with super().doc(param_name)) for the help button on GUI,
        specifies the input type for the GUI layout (see ConfigGenInputDef),
        specifies the check string (see configobj package documentation for validator) for the check button on GUI

    Each DataWorker/DataInterface class can add additional parameters (required or optional) in the format
    {'required': {'req_param_1': {'doc': 'documentation',
                                 'input': 'input_definition function',
                                 'validate': 'check string for validator'
                                  },
                 'req_param_2': {...}
                 },
     'optional': {opt_param_1': {...}
                  }
     }

    Then, a call to super().update_config(self.cfg, additional_cfg) will update the class configuration.

    To utilize, specify a @classmethod with name set_config in the DataWorker/DataInterface class and include
     the additional_config and a call to update_config. Then, after the class definition put class.set_config()
     to call the class method which will setup the class configuration.

    Note: when building a DataWorker/DataInterface by inheriting from another, if you only need to change one
     parameter specification like the documentation you don't need the 'input' or 'validate' keys in the
     additional_config dictionary for that parameter.

    Note: a parameter should not be both required and optional (do not use same name for required and optional)
    """

    # Default Configuration Setup for all DataWorkers/DataInterfaces
    cfg = {'required': {},
           'optional': {}}

    @classmethod
    def get_doc(cls, parameter: str) -> str:
        """
        Get the documentation from interface iget* function for parameter
        :param parameter: parameter name for documentation lookup
        :return:
        """
        special_function_name, = [func for func in dir(cls) if func.startswith('iget')]
        special_function = getattr(cls, special_function_name)
        docstring = ''.join([docstring for docstring in re.split(':param |:return:', inspect.getdoc(special_function))
                             if docstring.startswith(parameter + ':')])
        return docstring

    @staticmethod
    def update_config(base_cfg: dict, additional_cfg: dict) -> dict:
        """
        Update configuration dictionary with additional configurations
        :param base_cfg: the configuration dictionary to be updated
        :param additional_cfg: the additional configurations dictionary
        :return:
        """
        # Dictionary format cfg[required/optional][parameter][documentation/input/check]
        return_cfg = deepcopy(base_cfg)
        for req_opt_key in list(return_cfg.keys()):
            if req_opt_key not in additional_cfg.keys():
                # Additional Configuration does not have a (required/optional) parameter
                continue
            for param_key in list(additional_cfg[req_opt_key].keys()):
                if param_key in return_cfg[req_opt_key].keys():
                    return_cfg[req_opt_key][param_key].update(additional_cfg[req_opt_key][param_key])
                else:
                    return_cfg[req_opt_key][param_key] = additional_cfg[req_opt_key][param_key]
        return return_cfg
