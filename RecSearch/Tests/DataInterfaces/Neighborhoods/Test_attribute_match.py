import unittest
import pandas as pd
from RecSearch.DataInterfaces.Neighborhoods.attribute_match import IXNeighborhoodAttributesExactMatch

class TestNeighborhoodAttributesMatch(unittest.TestCase):
    def setUp(self):
        self.Interface = IXNeighborhoodAttributesExactMatch()
        self.who = {'Index': 1234, 'Name': 'Ann', 'Job': 'Manager', 'Cookie': 'Sugar', 'Donut': 'Glazed'}
        self.possible = pd.DataFrame(data=[['Suzy', 'Programmer', 'Sugar', 'Glazed'],
                                           ['Jim', 'Clerk', 'Pecan', 'Glazed'],
                                           ['Joe', 'Accountant', 'Sugar', 'Boston'],
                                           ['Ron', 'Technician', 'Sugar', 'Glazed']],
                                     columns=['Name', 'Job', 'Cookie', 'Donut'],
                                     index=[5, 6, 7, 8])

    def test_interface(self):
        self.assertEqual(self.Interface.iget_neighborhood(self.who, self.possible, ['Cookie', 'Donut']),
                         [{'Index': 5}, {'Index': 8}])
