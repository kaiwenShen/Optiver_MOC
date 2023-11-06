'''
This script is designed for various helper functions for designing and testing factors
'''
import numpy as np
import json

testing_factors_OTS = {}
existed_factors = {}
factor_performance = {}


# def add_factor_to_testing(factor_name: str, factor_value: np.ndarray, test_type: str) -> None:
#     '''
#     This function will add the factors to the testing dictionary for testing purpose.

    
#     --------------------------------- Parameters Explanations ----------------------------------------
#     factor_name: A string that stands for the name of the factor, should be somewhat descriptive
#     factor_value: A numpy array stores the factor values
#     test_type: A string stands for the factor value is based on training set or testing set. The value
#     must be train or test
#     testing_factors: A dictionary that will store all the factors waiting to be tested
#     '''
#     testing_factors[f"{factor_name}_{test_type}"] = factor_value

#     with open('testing_factors.json', 'w') as json_file:
#         json.dump(testing_factors, json_file)


def add_factor_to_existed(factor_name: str, factor_value: np.ndarray, test_type: str) -> None:
    '''
    This function will add the passed factors to the existed factor dictionary.


    --------------------------------- Parameters Explanations ----------------------------------------
    factor_name: A string that stands for the name of the factor, should be somewhat descriptive
    factor_value: A numpy array stores the factor values
    test_type: A string stands for the factor value is based on training set or testing set. The value
    must be train or test
    existed_factors: A dictionary that will store all the passed factors.
    '''
    existed_factors[f"{factor_name}_{test_type}"] = factor_value

    with open('existed_factors.json', 'w') as json_file:
        json.dump(existed_factors, json_file)


def add_factor_performance(factor_name: str, factor_performance_score: np.ndarray, test_type: str) -> None:
    '''
    This function will add the performance scores of the passed factors to the existed factor performance dictionary.


    --------------------------------- Parameters Explanations ----------------------------------------
    factor_name: A string that stands for the name of the factor, should be somewhat descriptive
    factor_performance_score: A number ranging from [0,1] standing for Pearson Correlation Coefficient of the factor value to the target value
    test_type: A string stands for the factor value is based on training set or testing set. The value
    must be train or test
    '''
    factor_performance[f"{factor_name}_{test_type}"] = factor_performance_score

    with open('factor_performance.json', 'w') as json_file:
        json.dump(factor_performance, json_file)


def load_json(file_name):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)


def dump_json(dictionary, file_name):
    with open(file_name, 'w') as json_file:
        json.dump(dictionary, json_file)

def dump_json_factors(dictionary, file_name):
    # because np.ndarray is not json serializable
    for key in dictionary.keys():
        dictionary[key] = dictionary[key].tolist()
    with open(file_name, 'w') as json_file:
        json.dump(dictionary, json_file)

def load_json_factors(file_name):
    # load factor dictionary and convert the value to np.ndarray
    res = load_json(file_name)
    for key in res.keys():
        res[key] = np.array(res[key], dtype=np.float64)
    return res

def flatten_factor_value(factor_value_dictionary, factor_name):
    return {factor_name: np.array([item for sublist in list(factor_value_dictionary.values()) for item in sublist])}

def get_test_factors_performance(test_factors: dict, factor_performance: dict) -> dict:
    '''
    This function will return the performance score of all the passed factors.


    --------------------------------- Parameters Explanations ----------------------------------------
    passed_factors: A dictionary stores all the passed factors, with key being the names of the factors and values being the factor values in np.ndarray
    factor_performance: A dictionary stores all the existed factors' performance score (in-sample correlation with target value)
    '''
    return {factor_name: factor_performance[factor_name] for factor_name in test_factors.keys()}

def get_num_passed_factors(passed_factors: dict) -> int:
    '''
    This function will return the number of passed factors.


    --------------------------------- Parameters Explanations ----------------------------------------
    passed_factors: A dictionary stores all the passed factors, with key being the names of the factors and values being the factor values in np.ndarray
    '''
    return len([factor_name for factor_name in passed_factors.keys() if sum(passed_factors[factor_name]) == len(passed_factors[factor_name])])

def add_factor_to_OTS_test(factor_name: str) -> None:
    '''
    This function will add the factors to the testing dictionary for testing purpose.


    --------------------------------- Parameters Explanations ----------------------------------------
    factor_name: A string that stands for the name of the factor, should be somewhat descriptive
    factor_value: A numpy array stores the factor values
    '''
    # load testing_factors_OTS json file
    testing_factors_OTS = load_json('./testing_factors_OTS.json')
    testing_factors_OTS[factor_name] = []

    with open('testing_factors_OTS.json', 'w') as json_file:
        json.dump(testing_factors_OTS, json_file)

def ols_res(x,y,fraction):
    beta = np.dot(x,y)/np.dot(x,x)
    return y-fraction*beta*x
