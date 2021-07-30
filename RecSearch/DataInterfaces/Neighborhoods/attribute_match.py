from RecSearch.DataInterfaces.Neighborhoods.Abstract import INeighborhoodAttributes
import pandas as pd


class IXNeighborhoodAttributesExactMatch(INeighborhoodAttributes):
    """Exactly matches attributes to find neighbors."""
    def iget_neighborhood(self, who: dict, possible: pd.DataFrame, attributes: list) -> list:
        match_dict = {attr: who[attr] for attr in attributes}
        return self.to_dicts(possible.loc[
                                (possible[list(match_dict)] == pd.Series(match_dict)).all(axis=1)
                            ][[]].itertuples())
