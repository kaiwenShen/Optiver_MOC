'''
Make sure this script is under the same folder with df_factor_train_data.csv and existed_factors.json files!

In this template we provide you with a general structure for developing factors and testing them in-sample. For the purpose of consistency, we design 
this framework following the testing environment of this competition on Kaggle. We will give you one date_id and one seconds_in_bucket each time 
(an interval) for you to design, calculate and test your factors in-sample. At the end of the loop, we concatenate the next interval to the current 
dataset for the next loop.

'''

# import pandas as pd
# import numpy as np
from time import time
# import logging
# import utils
# import json

def run_factor_value(df_train_dic_sorted, factor_function, factor_name):
    ### PLEASE DON'T MODIFY THE FOLLOWING CODE!
    # uncomment this once have the existed_factors.json file
    # factors_dict = json.load(existed_factors)
    # factors_dict = dict()
    # df_train = pd.read_csv("../research_train_set.csv") # This would take around 6 seconds, YOU SHALL ONLY READ THIS ONCE and save it for re-use purpose
    # no warming version

    # num_dates = df_train["date_id"].nunique()  # this number should be 401
    # num_seconds_in_bucket = df_train["seconds_in_bucket"].nunique()  # this number should be 55
    num_dates = 401
    num_seconds_in_bucket = 55

    # The above two lines will be REMOVED during the testing environment of the Optiver competition on Kaggle

    # # Designed for mapping dataframe columns using column name to numpy array



    # IO is expensive, might as well just compute it in memory

    '''
    As the time of concatenation operation for pandas csv or numpy array increases exponentially, 
    we pre-define a 10-year numpy array to save all the test data coming in the order of time interval
    '''
    # hist_list = []
    all_test = {}
    final_factor_value = {}

    # overhead_start = time()
    # df_train['slice_index'] = df_train['date_id'].astype(str) + '_' + df_train['seconds_in_bucket'].astype(str)  # 3 seconds
    # df_train_dic_sorted = df_train.drop(columns=['target']).groupby('slice_index').agg(lambda x: x.tolist()).to_dict('index')  # 1min
    # overhead_end = time()

    # overhead_time = overhead_end - overhead_start
    # print(f"Time used for tranforming training dataframe into dictionary: {overhead_time} seconds")

    time_start = time()
    print(f"Start calculating factor {factor_name}")
    for date_id in range(num_dates):
        for seconds_in_bucket in range(num_seconds_in_bucket):
            '''
            Since the test datasets will be given with the order of, under each date_id, each seconds_in_bucket will be given,
            we use a double-loop here. DON'T MODIFY the FOLLOWING CODE!
            '''
            seconds_in_bucket = seconds_in_bucket * 10 # will be REMOVED
            # The new_test_data will be replaced by the test dataset iterated during the Optiver test environment
            # THIS PART WILL NEED MODIFICATION SINCE WE ONLY HAVE test df in Optiver test environment, change to dict needs time on each interval
            # time_start_query = time()
            new_test_data = df_train_dic_sorted[f'{date_id}_{seconds_in_bucket}']
            # time_end_query = time()
            # print(f"On {date_id} and {seconds_in_bucket} Read df Used: {time_end_query - time_start_query} seconds")
            # time_paste_data_start = time()
            all_test[f'{date_id}_{seconds_in_bucket}'] = new_test_data # just a new key value pair for the dictionary, O(1)
            # time_paste_data_end = time()
            # print(f"On {date_id} and {seconds_in_bucket} Read df Used: {time_paste_data_end - time_paste_data_start} seconds")

            # time_factor_calc_start = time()
            final_factor_value[f'{date_id}_{seconds_in_bucket}'] = factor_function(current_data=all_test[f'{date_id}_{seconds_in_bucket}'])
            # time_factor_calc_end = time()
            # print(f"On {date_id} and {seconds_in_bucket} Read df Used: {time_factor_calc_end - time_factor_calc_start} seconds")
        if date_id % 100 == 0:
            print(f"Finished calculating factor {factor_name} for {date_id} dates")
    time_end = time()

    time_used_for_factor_calculating = time_end - time_start
    time_threshold = 300
    if time_used_for_factor_calculating >= time_threshold:
        # Factor calculation time cannot exceed 5 mins
        print(f"Time Limit Error!!: Used {time_used_for_factor_calculating:.2f} seconds for calculation factors. The limit is {time_threshold} seconds.")
    else:
        print (f"Accepted!!: Used {time_used_for_factor_calculating:.2f} seconds for calculation factors. The limit is {time_threshold} seconds.")
    return final_factor_value