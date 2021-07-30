import unittest
import pandas as pd
from RecSearch.DataInterfaces.Neighborhoods.global_all import IXGlobalNeighborhood

class TestGlobalNeighborhood(unittest.TestCase):
    def setUp(self):
        self.Interface = IXGlobalNeighborhood()
        self.who = {'Index': 1234, 'other': 'additional'}
        self.possible = pd.DataFrame(data=[['Suzy', 'Programmer'], ['Jim', 'Clerk'], ['Joe', 'Accountant']],
                                     columns=['Name', 'Job'],
                                     index=[5, 6, 7])

    def test_interface(self):
        self.assertEqual(self.Interface.iget_neighborhood(self.who, self.possible),
                         [{'Index': 5}, {'Index': 6}, {'Index': 7}])
