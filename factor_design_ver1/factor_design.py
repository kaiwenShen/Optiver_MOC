'''
Make sure this script is under the same folder with df_factor_train_data.csv and existed_factors.json files!

In this template we provide you with a general structure for developing factors and testing them in-sample. For the purpose of consistency, we design 
this framework following the testing environment of this competition on Kaggle. We will give you one date_id and one seconds_in_bucket each time 
(an interval) for you to design, calculate and test your factors in-sample. At the end of the loop, we concatenate the next interval to the current 
dataset for the next loop.

'''

import pandas as pd
import numpy as np
from time import time
import utils
import json
### PLEASE DON'T MODIFY THE FOLLOWING CODE!
# uncomment this once have the existed_factors.json file
# factors_dict = json.load(existed_factors)
factors_dict = dict()
df_train = pd.read_csv("../research_train_set.csv") # This would take around 6 seconds, YOU SHALL ONLY READ THIS ONCE and save it for re-use purpose
# no warming version
num_dates = df_train["date_id"].nunique()  # this number should be 401
num_seconds_in_bucket = df_train["seconds_in_bucket"].nunique()  # this number should be 55

# The above two lines will be REMOVED during the testing environment of the Optiver competition on Kaggle

# # Designed for mapping dataframe columns using column name to numpy array
# with open('col2index_map.json', 'r') as json_file:
#     col2index_map = json.load(json_file) # this map will map the column name of the dataframe to column index of numpy array

# IO is expensive, might as well just compute it in memory
col2index_map = {key: value for (key, value) in zip(df_train.columns, range(len(df_train.columns)))}

def factor(current_data: dict, hist_list: list) -> np.ndarray:
    '''
    This will be the main function to design your factors for the competition. Please
    define only one factor here each time. We provide you with:

    Current_data: a dictionary in the format of {column_name: column_value}, where column_name is from the original
    dataframe

    hist_list: A list for you to save the previous factor values (optional). For instance,
    if you are calculating a 100-day Moving Average (MA), then you can save the first calculated
    MA in hist_list, and then for the next MA calculation, you can use the saved ones.
    '''
    ###################### ADD YOUR CODE HERE FOR FACTORS DESIGN ######################
    # convert the current_data to your choice of numpy or pandas dataframe
    # current_data = pd.DataFrame(current_data)
    if len(hist_list)==0:
        hist_list.append(True)
    if hist_list[0]:
        current_data = np.array(list(current_data.values()),dtype=object).T  # this is faster than pd.DataFrame(current_data).values
        res = current_data[:, col2index_map['ask_price']] - current_data[:, col2index_map['bid_price']]
        return res # The return value MUSE BE a numpy array
    else:
        raise NotImplementedError("You need to implement the factor design function")
    ####################################################################################

'''
As the time of concatenation operation for pandas csv or numpy array increases exponentially, 
we pre-define a 10-year numpy array to save all the test data coming in the order of time interval
'''
hist_list = []
current_row = 0 # this is the tracker to track which row we are currently at
all_test = {}
testing_factor = {}
final_factor_value = {}

overhead_start = time()
df_train['slice_index'] = df_train['date_id'].astype(str) + '_' + df_train['seconds_in_bucket'].astype(str)  # 3 seconds
df_train_dic_sorted = df_train.drop(columns=['target']).groupby('slice_index').agg(lambda x: x.tolist()).to_dict('index')  # 1min
overhead_end = time()

overhead_time = overhead_end - overhead_start

time_start = time()
print("Start calculating factors")
for date_id in range(num_dates):
    for seconds_in_bucket in range(num_seconds_in_bucket):
        '''
        Since the test datasets will be given with the order of, under each date_id, each seconds_in_bucket will be given,
        we use a double-loop here. DON'T MODIFY the FOLLOWING CODE!
        '''
        seconds_in_bucket = seconds_in_bucket * 10 # will be REMOVED
        # The new_test_data will be replaced by the test dataset iterated during the Optiver test environment
        # time_start_query = time()
        new_test_data = df_train_dic_sorted[f'{date_id}_{seconds_in_bucket}']
        # time_end_query = time()
        # print(f"On {date_id} and {seconds_in_bucket} Read df Used: {time_end_query - time_start_query} seconds")
        # time_paste_data_start = time()
        all_test[f'{date_id}_{seconds_in_bucket}'] = new_test_data # just a new key value pair for the dictionary, O(1)
        # time_paste_data_end = time()
        # print(f"On {date_id} and {seconds_in_bucket} Read df Used: {time_paste_data_end - time_paste_data_start} seconds")

        # time_factor_calc_start = time()
        final_factor_value[f'{date_id}_{seconds_in_bucket}'] = factor(current_data=all_test[f'{date_id}_{seconds_in_bucket}'],
                                                                                 hist_list=hist_list)
        # time_factor_calc_end = time()
        # print(f"On {date_id} and {seconds_in_bucket} Read df Used: {time_factor_calc_end - time_factor_calc_start} seconds")
        current_row = current_row + len(new_test_data)
    if date_id % 20 == 0:
        print(f"At date {date_id} now")
time_end = time()

time_used_for_factor_calculating = time_end - time_start
time_threshold = 300
if time_used_for_factor_calculating >= time_threshold:
    # Factor calculation time cannot exceed 5 mins
    print(f"Time Limit Error!!: Used {time_used_for_factor_calculating:.2f} seconds for calculation factors. The limit is {time_threshold} seconds.")
else:
    print(f"Accepted!!: Used {time_used_for_factor_calculating:.2f} seconds for calculation factors. The limit is {time_threshold} seconds.")
# test
