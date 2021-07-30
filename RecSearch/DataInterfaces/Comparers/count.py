from RecSearch.DataInterfaces.Comparers.Abstract import IComparer


class IXCount(IComparer):
    def iget_comparer(self, who: dict, metric: str, compare_to: str, length: int = None) -> dict:
        metrics = [key for key in who.keys() if key.startswith('M__' + metric)]
        compare_column = 'M__' + metric + 'R__' + compare_to
        output = {}
        for met in metrics:
            if length is None or not length:
                length = len(who[compare_column])
            output[met] = sum(who[met][:length])
        return output
