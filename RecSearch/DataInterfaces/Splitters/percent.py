from RecSearch.DataInterfaces.Splitters.Abstract import ISplitter
import math
import numpy as np
import pandas as pd


class IXPercentSplit(ISplitter):
    """
    Implements the DataSplitter Interface for percentage split.
    """
    def partitionRowAmounts(self, percents: dict, total_rows: int) -> dict:
        """
        Convert dict of percentage of rows to number of rows
        :param percents: dict of percentages
        :param total_rows: total number of rows in dataframe
        :return: dict of number of rows for each partition
        """
        partition_ints = {k: math.floor(v*total_rows) for k, v in percents.items()}
        rows_accounted = sum(partition_ints.values())
        if rows_accounted != total_rows:
            partition_ints[max(partition_ints, key=lambda key: partition_ints[key])] += total_rows - rows_accounted
        return partition_ints

    def randomPartitionRowIndices(self, partition_rows: dict, total_rows: int) -> dict:
        """
        Get indices, randomly, corresponding to number of rows in each partition
        :param partition_rows: Numbers of rows in each partition
        :param total_rows: Total number of rows in data
        :return: partition consisting of integer indices
        """
        unsorted_randoms = pd.DataFrame(data=np.random.rand(total_rows), columns=['Rand'])
        sorted_randoms_index = unsorted_randoms.sort_values(by=['Rand']).index
        total = 0
        index_range_pairs = {k: (total, total := total+v) for k, v in partition_rows.items()}
        partition_indices = {k: sorted_randoms_index[v[0]:v[1]] for k, v in index_range_pairs.items()}
        return partition_indices

    def randomDataSets(self, data: pd.DataFrame, partition_index: dict) -> dict:
        """
        Return datasets containing rows corresponding to indices in partition
        :param data: dataset to be split
        :param partition_index: partition of indices
        :return: tuple of datasets
        """
        data_sets = {k: data.iloc[v, :] for k, v in partition_index.items()}
        return data_sets

    def iget_splitter(self, data: pd.DataFrame, train: float, test: float, validate: float = None) -> dict:
        """
        Splits data into partitions based on how percentages.
        :param data: dataset to be split
        :param train: pct of data for train set
        :param test: pct of data for test set
        :param validate: pct of data for validate set
        :return:
        """
        if validate is not None:
            how = {'train': train, 'validate': validate, 'test': test}
        else:
            how = {'train': train, 'test': test}

        rows = data.shape[0]
        split_pct = sum(how.values())
        if split_pct != 1:
            print('Warning: data split percentages sum to ' + str(split_pct))
        row_amounts = self.partitionRowAmounts(how, rows)
        random_index_sets = self.randomPartitionRowIndices(row_amounts, rows)
        data_sets = self.randomDataSets(data, random_index_sets)
        return data_sets
