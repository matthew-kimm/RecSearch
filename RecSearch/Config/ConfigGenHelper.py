from RecSearch.Config.ConfigGenMeta import meta_data_objects


class ConfigHelper:
    """ConfigHelper gets help (documentation) for inputs."""
    def __init__(self):
        self.meta_dw, self.meta_di = meta_data_objects()

    def get_help_string(self, help_key: str) -> str:
        """
        Gets help string for input GUI key.
        :param help_key: GUI key for help button
        :return: help string
        """
        # Key format: :Worker/Interface:Required/Optional:dw(:di):help
        if ':Interface:' in help_key:
            __, req_opt, dw, di, param, __ = help_key.split(':')[1:]
            help_string = self.meta_di.get_help(dw, di, param, req_opt)
        else:
            __, req_opt, dw, param, __ = help_key.split(':')[1:]
            help_string = self.meta_dw.get_help(dw, param, req_opt)
        return help_string
