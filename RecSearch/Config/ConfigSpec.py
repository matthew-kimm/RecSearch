from configobj import ConfigObj
from RecSearch.Config.ConfigGenMeta import meta_data_objects


class ConfigSpecCreator:
    """
    Allows for creating a configspec file (for checking and type interpolation when reading file)
    configspec described in ConfigObj documentation
    """
    def __init__(self):
        self.meta_dw, self.meta_di = meta_data_objects()

    def construct_dw_spec(self, dw: str, dw_config: dict):
        """
        Create a ConfigObj to serve as the configspec for a DataWorker and its interface.
        :param dw: DataWorker
        :param dw_config: DataWorker class cfg dict
        :return:
        """
        name, = list(dw_config.keys())
        spec = {name: {}}
        spec[name].update(self.meta_dw.get_all_checks(dw))
        spec[name].pop('name')
        spec[name]['parameters'] = self.meta_di.get_all_checks(dw, dw_config[name]['method'])
        return ConfigObj(spec)
