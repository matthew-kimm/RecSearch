from RecSearch.DataInterfaces.Metrics.Abstract import IMetric


class IXRecommendedTaken(IMetric):
    def iget_metric(self, who: dict, rec_column: list, ir_column: str) -> dict:
        output = {}
        for rec in rec_column:
            rec = 'R__' + rec
            item_ratings = who[ir_column]
            recommended = who[rec]
            rec_taken = [int(key in item_ratings.keys()) for key in recommended]
            output[rec] = rec_taken
        return output
