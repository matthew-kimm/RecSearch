import unittest
import pandas as pd
from RecSearch.DataInterfaces.Recommenders.popular import IXPopularRecommend

class TestPopularRecommender(unittest.TestCase):
    def setUp(self):
        self.Interface = IXPopularRecommend()
        self.n_column = "Neighbor_Column"
        self.who = {'Index': 1234, 'N__' + self.n_column: [{'Index': 0}, {'Index': 1}, {'Index': 3}]}
        self.ir_column = "ItemRating_Column"
        self.possible = pd.DataFrame(data=[[{'MATH1': 4.0, 'COMM1': 3.0}],
                                           [{'MATH1': 2.7, 'SPN1': 3.0}],
                                           [{'MATH1': 3.0, 'JPN1': 2.0}],
                                           [{'MATH1': 3.0, 'COMM1': 3.0}],
                                           [{'MATH1': 4.0}]],
                                     columns=[self.ir_column],
                                     index=[0, 1, 2, 3, 4])
        self.items = ['MATH1', 'COMM1', 'SPN1']
        self.recommend = self.Interface.iget_recommendation(self.who, self.possible, self.n_column, self.ir_column)

    def test_interface(self):
        self.assertTrue(self.items == self.recommend)
