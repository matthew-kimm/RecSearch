from RecSearch.DataInterfaces.Neighborhoods.Abstract import INeighborhoodGradeAttributes
from RecSearch.DataInterfaces.Neighborhoods.attribute_match \
    import IXNeighborhoodAttributesExactMatch as SIXNeighborhoodAttributesExactMatch
from RecSearch.DataInterfaces.Neighborhoods.grade_match import IXGradeMatch as SIXGradeMatch
import numpy as np
import pandas as pd

# Note: SettingWithCopyWarning is the desired behavior (don't fix), do not want to change original df.
# Only allowed one IX**** (implemented) item per interface module for standardizing
# To build on or inherit from another IX call it SIX*** (super implemented)


class IXNeighborAttributesMatchOverlapGradeHistory(INeighborhoodGradeAttributes):
    # The below is to fix MRO (method resolution order) resolving to the attribute exact match
    @classmethod
    def set_config(cls):
        additional_config = {'required': {(key := 'attributes'): {'doc': super().get_doc(key),
                                                                  'input': 'columns()',
                                                                  'validate': 'string_list()'
                                                                   },
                                          (key := 'item_history_col'): {'doc': super().get_doc(key),
                                                                        'input': 'column()',
                                                                        'validate': 'string()'}

                                          }
                             }
        cls.cfg = super().update_config(cls.cfg, additional_config)

    def iget_neighborhood(self, who: dict, possible: pd.DataFrame, attributes: list, item_history_col: str) -> list:
        df = self.neighbor_filter(SIXNeighborhoodAttributesExactMatch.iget_neighborhood(self, who, possible, attributes), possible)
        return SIXGradeMatch.iget_neighborhood(self, who, df, item_history_col)

IXNeighborAttributesMatchOverlapGradeHistory.set_config()
