from RecSearch.DataInterfaces.Neighborhoods.Abstract import INeighborhood
import pandas as pd

class IXGlobalNeighborhood(INeighborhood):
    """Everyone is a neighbor."""
    def iget_neighborhood(self, who: dict, possible: pd.DataFrame) -> list:
        return self.to_dicts(possible[[]].itertuples())
