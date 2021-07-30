from RecSearch.DataInterfaces.Splitters.percent import IXPercentSplit
from RecSearch.Tests.DataInterfaces.Splitters.SharedTestSplitter import SharedTestSplitter
import unittest
import pandas as pd


class TestQuerySplitter(unittest.TestCase):
    def setUp(self):
        self.percents = {'train': 0.8, 'test': 0.2}
        self.Interface = IXPercentSplit()
        self.data = pd.DataFrame(data=[['Math', 2017, 3.6],
                                       ['Computer Science', 2017, 3.8],
                                       ['English', 2019, 2.7],
                                       ['Math', 2018, 2.0],
                                       ['Art', 2018, 3.1],
                                       ['Engineering', 2017, 3.4],
                                       ['Art', 2017, 3.5],
                                       ['Math', 2017, 2.8],
                                       ['English', 2018, 3.6],
                                       ['Art', 2018, 3.0]],
                                 columns=['Department', 'Year', 'GPA'],
                                 index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.split = self.Interface.iget_splitter(self.data, **self.percents)

    def checkPercent(self, datasets: dict):
        if set(self.percents.keys()) == set(datasets.keys()):
            compare = {key: (datasets[key].shape[0] / self.data.shape[0]) == percent
                       for key, percent in self.percents.items()}
            return all(compare.values())
        else:
            raise KeyError('Keys in dictionaries do not match')

    def checkPartition(self, datasets: dict):
        return pd.concat(datasets.values()).sort_index().equals(self.data)


    def test_interface_percent(self):
        self.assertTrue(self.checkPercent(self.split))

    def test_interface_partition(self):
        self.assertTrue(self.checkPartition(self.split))
