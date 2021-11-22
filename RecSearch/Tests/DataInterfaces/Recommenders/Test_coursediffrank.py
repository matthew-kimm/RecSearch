import unittest
import pandas as pd
from RecSearch.DataInterfaces.Recommenders.coursediffrank import IXCourseDiffRankRecommend

class TestCourseDiffRankRecommender(unittest.TestCase):
    def setUp(self):
        self.Interface = IXCourseDiffRankRecommend()
        self.n_column = "Neighbor_Column"
        self.who = {'Index': 1234, 'N__' + self.n_column: [{'Index': 0}, {'Index': 1}, {'Index': 3}]}
        self.ir_column = "ItemRating_Column"
        self.possible = pd.DataFrame(data=[[{'MATH2': 3.0, 'COMM2': 4.0, 'BIO2': 3.0, 'CHM2': 3.0, 'ART2': 1.7}],
                                           [{'MATH2': 2.7, 'COMM2': 3.0}],
                                           [{'MATH2': 3.0, 'JPN2': 2.0}],
                                           [{'MATH2': 2.7, 'COMM2': 3.0, 'CHM2': 2.7, 'ART2': 1.7}],
                                           [{'MATH2': 4.0}]],
                                     columns=[self.ir_column],
                                     index=[0, 1, 2, 3, 4])
        # Found using spreadsheet
        self.items = ['COMM2', 'BIO2', 'CHM2', 'MATH2', 'ART2']
        self.recommend = self.Interface.iget_recommendation(self.who, self.possible, self.n_column, self.ir_column,
                                                            0.95, 10e-6, 100)

    def test_interface(self):
        self.assertTrue(self.items == self.recommend)