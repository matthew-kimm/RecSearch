from RecSearch.DataInterfaces.Splitters.query import IXQuerySplit
from RecSearch.Tests.DataInterfaces.Splitters.SharedTestSplitter import SharedTestSplitter
import unittest
import pandas as pd


class TestQuerySplitter(SharedTestSplitter, unittest.TestCase):
    def setUp(self):
        self.Interface = IXQuerySplit()
        self.data = pd.DataFrame(data=[['Math', 2017, 3.6],
                                       ['Computer Science', 2017, 3.8],
                                       ['English', 2019, 2.7],
                                       ['Math', 2018, 2.0],
                                       ['Art', 2018, 3.1],
                                       ['Engineering', 2017, 3.4]],
                                 columns=['Department', 'Year', 'GPA'],
                                 index=[0, 1, 2, 3, 4, 5])
        self.data17 = self.data.loc[[0, 1, 5]]
        self.data1819 = self.data.loc[[2, 3, 4]]
        self.result = {'train': self.data17, 'test': self.data1819}

    def test_interface(self):
        self.assertTrue(self.compare_dict_dataframes(self.result,
                                                     self.Interface.iget_splitter(self.data,
                                                                                  **{'train': 'Year in [2017]',
                                                                               'test': 'Year in [2018, 2019]'})))
