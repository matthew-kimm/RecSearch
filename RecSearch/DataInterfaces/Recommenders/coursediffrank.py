import numpy as np
from RecSearch.DataInterfaces.Recommenders.Abstract import IMatrixRankRecommender
from itertools import combinations, permutations
import pandas as pd


class IXCourseDiffRankRecommend(IMatrixRankRecommender):
    def iget_recommendation(self, who: dict, possible: pd.DataFrame, n_column: str, ir_column: str, xi: float, tol: float, max_iter: int, filter_name: str = None) -> list:
        f = self.get_filter(who, filter_name)
        df = self.get_reduced_df(who, possible, n_column)
        df[ir_column] = df[ir_column].apply(lambda x: sorted(
            [(k, v) for k, v in x.items() if k not in f],
            key=lambda y: y[0]))
        # Get 2-Combos of student courses for pairwise comparison
        df[ir_column] = df[ir_column].apply(lambda x: list(combinations(x, 2)))
        # Format as (Course 1, Course 2, Course 1 Grade - Course 2 Grade)
        df[ir_column] = df[ir_column].apply(lambda x:
                                            [(y[0][0], y[1][0], y[0][1]-y[1][1]) for y in x if len(y) > 0])
        # Remove Empty Course-Ratings
        df = df[df[ir_column].apply(lambda x: len(x) > 0)]
        if df.empty:
            return []
        new_df = pd.DataFrame(list(df[ir_column].explode()), columns=['Course1', 'Course2', 'Diff'])
        new_df = new_df.dropna(subset=['Course1', 'Course2'])
        # Count Course 1 better than Course 2
        pos_df = new_df.groupby(['Course1', 'Course2'])['Diff'].agg(lambda x: sum(x > 0)).reset_index()
        # Count Course 1 worse than Course 2
        neg_df = new_df.groupby(['Course1', 'Course2'])['Diff'].agg(lambda x: sum(x < 0)).reset_index()

        # Get Course1 Union Course2 for index/columns to make square matrix
        all_courses = sorted(list(set(new_df['Course1'].unique()).union(set(new_df['Course2'].unique()))))
        # Create dummy data frame with all 2-permutations of index (square matrix)
        distance_df = pd.DataFrame(permutations(all_courses, r=2), columns=['Course1', 'Course2'])
        # Merge and pivot (courses are sorted, idx=Course1)
        pos_distance_df = pd.merge(distance_df, pos_df, how='left', on=['Course1', 'Course2']).fillna(0)
        positive_matrix = pos_distance_df.pivot(index=['Course1'], columns=['Course2'], values=['Diff'])
        # Merge and pivot (courses are sorted, idx=Course2)
        neg_distance_df = pd.merge(distance_df, neg_df, how='left', on=['Course1', 'Course2']).fillna(0)
        negative_matrix = neg_distance_df.pivot(index=['Course2'], columns=['Course1'], values=['Diff'])
        # Positive Matrix (i,j) for j > i => # Course i (outperform) Course j
        # Negative Matrix (i,j) for i > j => # Course i (outperform) Course j
        # Voting scheme is Course X points to Course Y when Y outperforms X (need transpose)
        matrix = (positive_matrix.T + negative_matrix.T)
        matrix = matrix.fillna(0)
        matrix.index = matrix.columns
        # Get proportion (i,j) is the proportion of times Course j outperform Course i
        matrix = (matrix / (matrix + matrix.T)).fillna(0)
        # Divide by row sums
        matrix = matrix / np.array(matrix).sum(1, keepdims=True)
        # Fill Empty Rows (courses that are not outperformed) with equal link out
        matrix = matrix.fillna(1/matrix.shape[1])
        matrix = self.addTeleportation(matrix, xi)
        # Iterate with column stochastic matrix (take transpose) to match existing function
        v = self.powerIteration(matrix.T, tol, max_iter, matrix.index, norm=False)
        courses = self.sortedResult(v)
        return courses
