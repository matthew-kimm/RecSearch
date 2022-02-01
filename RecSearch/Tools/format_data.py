"""
Formats data for use in RecSearch program (multi-table relations turned into single table using Python list/dicts)
"""
from RecSearch import GetProgramLocation
import argparse
import pandas as pd


def main(attribute_csv, item_history_csv, target_term, output_file):
    if attribute_csv:
        attribute_data = pd.read_csv(attribute_csv, index_col=0)
    item_history_data = pd.read_csv(item_history_csv)
    item_history_data['Item'] = item_history_data['Item'].astype(str)

    item_history_data['ItemRating'] = pd.Series(data=list(zip(item_history_data['Item'], item_history_data['Rating'])),
                                                index=item_history_data.index)

    item_history_data['Term'] = item_history_data['Term'].astype(int)
    item_history = item_history_data[item_history_data['Term'] < int(target_term)]
    item_recommend = item_history_data[item_history_data['Term'] >= int(target_term)]

    def flatten(df, out_column_name):
        flat_df = df.groupby('Index').agg(**{out_column_name: pd.NamedAgg('ItemRating', lambda x: dict(list(x)))})
        return flat_df

    item_history = flatten(item_history, 'Item_History')
    item_recommend = flatten(item_recommend, 'Item_Rating')

    if attribute_csv:
        output_df = attribute_data.join(item_history, how='left').join(item_recommend, how='left')
    else:
        output_df = item_history.join(item_recommend, how='left')

    output_df.to_csv(output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Flattens item history data and combines with user attribute data.')
    parser.add_argument('attribute_data',
                        help='CSV Data, 1 set of attributes per index, (Index, Attribute Columns ...)')
    parser.add_argument('item_history_data', help='CSV Data (Index, Item, Rating (Numerical), Term (Coded))')
    parser.add_argument('target_coded_term', help='Number of target (recommend) term, first possible term = 0, ...')
    parser.add_argument('output_file', help='File location for CSV output (Index, Item_History, Item_Rating, Attributes ...)')
    args = parser.parse_args()

    attribute_csv = args.attribute_data
    item_history_csv = args.course_history_data
    target_term = args.target_coded_term
    output_file = args.output_file
    main(attribute_csv, item_history_csv, target_term, output_file)
