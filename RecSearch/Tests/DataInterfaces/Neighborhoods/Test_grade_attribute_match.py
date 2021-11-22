import unittest
import pandas as pd
from RecSearch.DataInterfaces.Neighborhoods.grade_attribute_match import IXNeighborAttributesMatchOverlapGradeHistory

class TestNeighborhoodGradeAttributesMatch(unittest.TestCase):
    def setUp(self):
        self.Interface = IXNeighborAttributesMatchOverlapGradeHistory()
        self.who = {'Index': 1234, 'College': 'Science', 'Applicant_Tier': 4,
                    'Grade_History': {'MATH1': 3.0, 'COMM2': 2.0, 'ART1': 3.0}}
        self.possible = pd.DataFrame(data=[['Science', 4, {'MATH1': 3.0, 'COMM2': 2.0}],
                                           ['Science', 4, {'MATH1': 3.0}],
                                           ['Science', 4, {'MATH1': 3.3, 'COMM2': 1.7, 'ART1': 4.0}],
                                           ['Science', 3, {'MATH1': 3.0}],
                                           ['Art', 4, {'MATH1': 3.0}],
                                           ['Art', 2, {}],
                                           ['Science', 4, {}]],
                                     columns=['College', 'Applicant_Tier', 'Grade_History'],
                                     index=[5, 6, 7, 8, 9, 10, 11])

    def test_exact_grade_match(self):
        self.assertEqual(self.Interface
                         .iget_neighborhood(self.who, self.possible,
                                            ['College', 'Applicant_Tier'], 'Grade_History', True),
                         [{'Index': 5, 'Common_GPA': 2.5}, {'Index': 6, 'Common_GPA': 3.0}])

    def test_letter_grade_match(self):
        self.assertEqual(self.Interface
                         .iget_neighborhood(self.who, self.possible,
                                            ['College', 'Applicant_Tier'], 'Grade_History', False),
                         [{'Index': 5, 'Common_GPA': 2.5}, {'Index': 6, 'Common_GPA': 3.0},
                          {'Index': 7, 'Common_GPA': 2.5}])
