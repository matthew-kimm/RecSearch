"""
Precomputes the filter for the onfly_boolean format
"""
from RecSearch import GetProgramLocation
import argparse
import ast
import pandas as pd
from RecSearch.DataInterfaces.Filters.onfly_boolean import IXFilterOnFly


def main(data: str, filter_file: str, output_file: str):
    df = pd.read_csv(data, index_col=0)
    for column in df.columns:
        df[column] = df[column].apply(lambda x: ast.literal_eval(x))

    filter_interface = IXFilterOnFly()
    output_df = pd.DataFrame(columns=[df.index.name, 'Filter'])
    for who in df.itertuples():
        who = who._asdict()
        print(who['Index'])
        filter_list = filter_interface.iget_filter(who, None, 'Item_History', filter_file, 2.0)
        output_df = output_df.append({df.index.name: who['Index'], 'Filter': filter_list}, ignore_index=True)

    output_df.to_csv(output_file, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates Filter Lists before Run')
    parser.add_argument('course_history_data', help='CSV Data (Index and Item_History)')
    parser.add_argument('filter_file', help='CSV Filter Data (Course, Condition, Replace, Implies)')
    parser.add_argument('output_file', help='File location for CSV output (Index, Filter)')
    args = parser.parse_args()

    data = args.course_history_data
    filter_file = args.filter_file
    output_file = args.output_file

    main(data, filter_file, output_file)
