from configobj import ConfigObj
from RecSearch.Config.ConfigSpec import ConfigSpecCreator
from RecSearch.Config.ConfigGenMeta import meta_data_objects
from RecSearch.Config.ConfigValidator import default_validator


class ExperimentParameters:
    """
    ExperimentParameters class manages parameters for the experiment.
    """
    def __init__(self, configfile: str, alternative: bool = False):
        self.validator = default_validator
        self.meta_dw, self.meta_di = meta_data_objects()
        self.Spec = ConfigSpecCreator()
        self.Config = ConfigObj(configfile)
        self.Config = self.interpolate(alternative)
        self.check_config()

    def cfg(self):
        return self.Config

    def interpolate(self, alternative):
        """
        Converts text from config file to proper type float, int, etc.
        :param alternative: Load without DW_ in name for the ConfigGenerator
        :return:
        """
        # ConfigObj with ConfigSpec does not seem to work as intended
        # so have to implement the idea with for loops (messy)
        output = {}
        for key in self.Config.keys():
            output[key] = {}
            if key.startswith('DW_'):
                dw = key.split('DW_')[1]
                for name_key, name_config in self.Config[key].items():
                    if isinstance(name_config, dict):
                        output[key][name_key] = {}
                        output[key][name_key]['name'] = name_key
                        spec = ConfigSpecCreator.construct_dw_spec(self, dw, {name_key: name_config})
                        for param_key, param in self.Config[key][name_key].items():
                            if isinstance(param, dict):
                                output[key][name_key][param_key] = {}
                                for sub_key, sub in param.items():
                                    output[key][name_key][param_key][sub_key] = \
                                        self.validator.check(spec[name_key][param_key][sub_key], sub)
                            else:
                                output[key][name_key][param_key] = self.validator.check(spec[name_key][param_key], param)
                    else:
                        output[key][name_key] = self.validator.check(self.meta_dw.get_any_check(dw, name_key), name_config)
            else:
                output[key] = self.Config[key]
        if alternative:
            alt_output = {k: v for k, v in output.items() if not k.startswith('DW_')}
            alt_output.update({k.removeprefix('DW_'): v for k, v in output.items() if k.startswith('DW_')})
            output = alt_output
        return output

    def check_config(self):
        # Check to make sure valid config file
        # Use configobj validator and specific validation (e.g. recommender must have a neighborhood)
        # This is a higher level of config checking to make sure the config "makes sense"
        # Not implemented
        pass
