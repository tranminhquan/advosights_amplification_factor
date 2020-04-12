import pandas as pd
import numpy as np

af_df = pd.read_csv('Milk_2/AF_score/af_raw_data.csv')

af_df = (af_df
         .groupby(['to_user'])
         .agg({'AF score': 'mean', 'fid':'count'})
         .reset_index()
         .sort_values(['AF score'], ascending=False)
         .rename({'to_user': 'from_user', 'fid': 'count'}, axis='columns'))


af_df.to_csv('af_scr.csv')