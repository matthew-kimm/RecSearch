from RecSearch.DataInterfaces.Recommenders.Abstract import IMatrixRecommender
import pandas as pd


class IXHITSRecommend(IMatrixRecommender):
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, n_column: str, ir_column: str,
                            req_rating: float, xi: float, tol: float, max_iter: int, filter_name: str = None) -> list:
        f = self.get_filter(who, filter_name)
        df = self.get_reduced_df(who, possible, n_column)
        df[ir_column] = df[ir_column].apply(lambda x: [';'.join((k, str(v))) for k, v in x.items() if k not in f])
        # Exploding on [] results in nan
        df = df.explode(column=ir_column).dropna()
        if df.empty:
            return []
        else:
            df[['Item', 'Rating']] = df[ir_column].str.split(pat=';', expand=True)
            df['Rating'] = df['Rating'].astype(float)
            df = df[df['Rating'] >= req_rating]
            df['Rating'] = 1
            anames = list(df['Item'].sort_values().unique())
            hnames = list(df.index.unique())
            matrix = self.createAdjacencyMatrix(df, ['Item'], ['Rating'])
            matrix = self.createBipartiteHITSMatrix(matrix)
            matrix = self.addTeleportation(matrix, xi)
            auth = self.powerIteration(matrix, tol, max_iter, anames)
            # add hub?
            return self.sortedResult(auth)
