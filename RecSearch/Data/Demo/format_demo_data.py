import pandas as pd
import math
import numpy as np
import csv

df = pd.read_csv('Movie/movie.csv', sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp'])


def time_split(s: pd.Series) -> pd.Series:
    n = len(s)
    future_length = math.ceil(n/2)
    future_indicator = np.zeros(n)
    future_indicator[future_length:] = 1
    history_future_map = pd.Series(index=s.sort_values().values, data=future_indicator).to_dict()
    return s.map(history_future_map)


df['timestamp'] = df.groupby('user_id')['timestamp'].transform(time_split)

df = df.rename(columns={'user_id': 'Index', 'item_id': 'Item', 'rating': 'Rating', 'timestamp': 'Term'})

df['Item'] = df['Item'].astype(str)
df.to_csv('Movie/formatted_movie_data.csv', quoting=csv.QUOTE_NONNUMERIC, index=False)

