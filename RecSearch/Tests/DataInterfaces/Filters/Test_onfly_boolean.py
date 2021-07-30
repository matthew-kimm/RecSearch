import unittest
import pandas as pd
from RecSearch.DataInterfaces.Filters.onfly_boolean import IXFilterOnFly

class TestFilterFile(unittest.TestCase):
    def setUp(self):
        self.Interface = IXFilterOnFly()
        self.who = {'Index': 1234, 'Course_History': {'b': 3.0, 'w': 1.0, 'v': 2.7, 'd': 4.0}}
        self.filter_df = pd.DataFrame(data=[['x', '', [], []],
                                            ['y', '', [], []],
                                            ['z', '', [], []],
                                            ['u', '', [], []],
                                            ['v', '', ['u'], ['u']],
                                            ['w', '', [], []],
                                            ['d', 'v', ['v'], ['u', 'v']],
                                            ['e', 'w', ['w'], ['w']],
                                            ['c', 'x', ['x'], ['x']],
                                            ['b', 'x|y', ['x', 'y'], ['x', 'y']],
                                            ['a', 'x&y&z', ['x', 'y', 'z'], ['x', 'y', 'z']]],
                                      columns=['Course', 'Condition', 'Replace', 'Implies']
                                      ).set_index('Course')

    def test_interface(self):
        self.assertEqual(set(self.Interface.iget_filter(self.who, pd.DataFrame, 'Course_History', self.filter_df, 2.0)),
                         set(['d', 'v', 'u', 'b', 'x', 'y', 'a', 'e']))
