from RecSearch.DataInterfaces.Splitters.Abstract import ISplitter
import pandas as pd


class IXQuerySplit(ISplitter):
    """Splits the data by using queries."""
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'train'): {
                                                           'validate': 'string()'
                                                            },
                                          (key := 'test'): {
                                                            'validate': 'string()'},
                                          },
                             'optional': {(key := 'validate'): {
                                                                'validate': 'string(default=None, disabled=True)'}
                                          }

                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    def iget_splitter(self, data: pd.DataFrame, train: float, test: float, validate: float = None) -> dict:
        if validate is not None:
            how = {'train': train, 'test': test, 'validate': validate}
        else:
            how = {'train': train, 'test': test}
        return {k: data.query(v) for k, v in how.items()}

IXQuerySplit.set_config()