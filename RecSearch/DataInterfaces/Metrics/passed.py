from RecSearch.DataInterfaces.Metrics.Abstract import IMetricThreshold

class IXRecommendedPassRate(IMetricThreshold):
    def iget_metric(self, who: dict, rec_column: list, ir_column: str, threshold: float) -> dict:
        output = {}
        for rec in rec_column:
            rec = 'R__' + rec
            item_ratings = who[ir_column]
            recommended = who[rec]
            passed = [int(key in item_ratings.keys() and item_ratings[key] >= threshold) for key in recommended]
            output[rec] = passed
        return output
