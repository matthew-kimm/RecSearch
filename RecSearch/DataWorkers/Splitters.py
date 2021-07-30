from RecSearch.DataWorkers.Abstract import GeneralDataWorkers


class Splitters(GeneralDataWorkers):
    """
    Splitters class splits dataset.
    """
    # Configs inline with [[NAME]]
    @classmethod
    def set_config(cls):
        additional_config = {'required': {'name': {'input': 'text(disabled=True)',
                                                   'validate': 'string(default="Default")'},
                                          'precedence': {'doc': 'Order (ascending) to run dataworkers',
                                                         'input': 'text(disabled=True)',
                                                         'validate': 'integer(default=0)'
                                                         }}}
        cls.cfg = super().update_config(cls.cfg, additional_config)

    def __init__(self, name: str, data_worker_config: dict):
        self.class_name = self.get_classname()
        super().__init__(self.class_name, name, data_worker_config)

    @classmethod
    def get_classname(cls):
        return cls.__name__


Splitters.set_config()
