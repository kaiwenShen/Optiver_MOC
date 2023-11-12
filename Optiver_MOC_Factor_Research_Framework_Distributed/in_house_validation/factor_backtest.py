'''
This script will serve as the framework for factors testing. The helper methods will be added on demand. One can use this for in-sample fitting and testing, and
we will use this for out-of-sample testing.

existed_factors: A dictionary stored all the passed factors, with key being the names of the factors and values being the factor values in np.ndarray
testing_factors: A dictionary stored all the factors waited for the testing, with the same format of existed_factors
factor_performance: A dictionary stored all the existed factors' performance score (in-sample correlation with target value)
'''
import numpy as np
# import utils
from datetime import datetime
import glob
import json

from Optiver_MOC.Optiver_MOC_Factor_Research_Framework_Distributed.in_house_validation import utils

target_on_train = np.load('./in_house_validation/target_on_train.npy')
target_on_train[np.isnan(target_on_train)] = 0
target_on_test = np.load('./in_house_validation/target_on_test.npy')
target_on_test[np.isnan(target_on_test)] = 0

class Factor_Backtest:
    def __init__(self, existed_factors: dict, testing_factors: dict, factor_performance: dict):
        self.insample_corr = None
        self.existed_factors = existed_factors
        self.testing_factors = testing_factors
        self.factor_performance = factor_performance
        self.passed_factors = {}

    def check_in_sample_performance(self, factor_name: str, factor_value: np.ndarray):
        '''
        The new factor should perform in-sample with Pearson correlation coefficient > 0.05 with target value
        '''
        corr_coef_threshold = 0.05
        corr_coef = np.corrcoef(factor_value, target_on_train)[0, 1]
        self.passed_factors[factor_name] = []
        self.factor_performance[factor_name] = corr_coef
        print('\n_______________________________________Factor Performance_______________________________________________________')
        if corr_coef > corr_coef_threshold:
            # this factor pass this step
            print(f"Factor {factor_name} PASSED in-sample performance check with correlation coefficient {corr_coef}")
            self.passed_factors[factor_name].append(1)
        else:
            print(f"Factor {factor_name} FAILED in-sample performance check with correlation coefficient {corr_coef}")
            self.passed_factors[factor_name].append(0)

    def check_in_sample_corr(self, factor_name: str, factor_value: np.ndarray):
        '''
        For each testing factor, we examine whether it has a correlation coefficient:
        1. Less than 0.4 with all of the existed factors: the testing factor passed
        2. Between 0.4 and 0.7 with some existed factor: the in-sample performance of the new factor
        needs to be better than 1.2x the in-sample performance of this old factor
        3. Larger than 0.7 with some existed factor: the in-sample performance of the new factor
        needs to be better than 1.4x the in-sample performance of this old factor
        '''
        print('\n___________________________________Factor pairwise Correlation__________________________________________________')
        corr_factors = {}
        threshold_1 = 0.4
        threshold_2 = 0.7
        performance_threshold_1 = 1.4
        performance_threshold_2 = 1.2
        corr_factors[factor_name] = {}
        for old_factor_name, old_factor_value in self.existed_factors.items():
            corr_coef = np.corrcoef(factor_value, old_factor_value)[0, 1]
            corr_factors[factor_name][old_factor_name] = corr_coef
            if corr_coef < threshold_1:
                # pass directly for this existed factor
                continue
            elif threshold_1 <= corr_coef < threshold_2:
                # need further check
                if self.factor_performance[factor_name] > corr_coef * performance_threshold_1 * self.factor_performance[
                    old_factor_name]:
                    # pass for this existed factor
                    continue
                else:
                    self.passed_factors[factor_name].append(0)
                    print(f'Factor {factor_name} FAILED in-sample correlation check with factor {old_factor_name}, \nThe pair have correlation {corr_coef}')
                    print(f'This falls in type 1 threshold, from {threshold_1} to {threshold_2}.\n'
                          f'The required performance is {performance_threshold_1} times the old factor performance {self.factor_performance[old_factor_name]} times correlation {corr_coef} = {corr_coef * performance_threshold_1 * self.factor_performance[old_factor_name]}.')
                    print('Performance of the new factor now is ', self.factor_performance[factor_name])
                    return None
            else:
                # need further check
                if self.factor_performance[factor_name] > performance_threshold_2 * self.factor_performance[
                    old_factor_name]:
                    # pass for this existed factor
                    continue
                else:
                    self.passed_factors[factor_name].append(0)
                    print(f'Factor {factor_name} FAILED in-sample correlation check with factor {old_factor_name}, \nThe pair have correlation {corr_coef}')
                    print(f'This falls in type 2 threshold, >{threshold_2}\n')
                    print(f'The required performance is {performance_threshold_2} times the old factor performance {self.factor_performance[old_factor_name]} = {performance_threshold_2 * self.factor_performance[old_factor_name]}.')
                    print('Performance of the new factor now is ', self.factor_performance[factor_name])
                    return None
        # this new factor pass for all existed factors check
        self.passed_factors[factor_name].append(1)
        print(f"Factor {factor_name} passed in-sample pairwise correlation check with all existed factors")
        # print(f"Factor {factor_name} has in-sample performance with all existed factors as below:")
        # print(json.dumps(corr_factors[factor_name], indent=4))
        print('______________________________________________________________________________________________')

    def run_testing(self):
        '''
        We will check the factor performance followed by the above three steps
        '''
        pass_factors_list = []
        failed_factors_list = []
        for factor_name, factor_value in self.testing_factors.items():
            print(f"Start testing factor: {factor_name}..........")
            print('==============================================================================================================')
            self.check_in_sample_performance(factor_name, factor_value)
            self.check_in_sample_corr(factor_name, factor_value)
            print('\n_______________________________________Factor Conclusion_______________________________________________________')
            if sum(self.passed_factors[factor_name]) == 2:
                print(f"Factor {factor_name} passed all the tests, and will be added to the factors for out-of-sample testing")
                # utils.add_factor_to_OTS_test(factor_name=factor_name)
                pass_factors_list.append(factor_name)
            else:
                failed_factors_list.append(factor_name)
                print(f"Factor {factor_name} failed one of the tests, and will not be added to the factors for out-of-sample testing")
            print('==============================================================================================================')
        print('\n')
        print('______________________________________Overall Conclusion________________________________________________________')
        print(f"Factors passed all the tests: {pass_factors_list}")
        print(f"Factors failed at least one of the tests: {failed_factors_list}")
        return pass_factors_list

    def run_out_of_sample(self, factor_name, factor_data, target_data):
        out_of_sample_corr = np.corrcoef(factor_data, target_data)[0, 1]
        print(f"Out of sample correlation coefficient for factor {factor_name} is {out_of_sample_corr}")
        if out_of_sample_corr >= 0.05 or out_of_sample_corr >= 0.7 * self.factor_performance[factor_name]:
            print(
                f"Factor {factor_name} passed out-of-sample performance \n in-sample corr = {self.factor_performance[factor_name]} \n out-of-sample corr = {out_of_sample_corr}")
            return True
        else:
            print(
                f"Factor {factor_name} failed out-of-sample performance \n in-sample corr = {self.factor_performance[factor_name]} \n out-of-sample corr = {out_of_sample_corr}")
            print(f"threshold is {min(0.05, 0.7 * self.factor_performance[factor_name])}")
            return False
    def enter_into_factor_pool(self, factor_name,factor_train_data,factor_test_data):
        # first, in this object, we add the factor into the existed_factors
        self.existed_factors[factor_name] = factor_train_data
        # # then we find if there is a temp factor pool, if not, we create one
        today = str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day)
        file_pattern = f'./in_house_validation/tmp{today}.json'
        file_pattern_test = f'./in_house_validation/test_tmp{today}.json'
        match_files = glob.glob(file_pattern)
        match_files_test = glob.glob(file_pattern_test)
        if len(match_files) == 0:
            print('No temporary files found, creating one')
            temp_factor_pool_train = {}
            temp_factor_pool_test = {}
            temp_factor_pool_train[factor_name] = factor_train_data
            temp_factor_pool_test[factor_name] = factor_test_data
            utils.dump_json_factors(temp_factor_pool_train, file_pattern)
            utils.dump_json_factors(temp_factor_pool_test, file_pattern_test)
        else:
            print('Temporary files found, appending to the existed one')
            temp_factor_pool_train = utils.load_json_factors(file_pattern)
            temp_factor_pool_test = utils.load_json_factors(file_pattern_test)
            temp_factor_pool_train[factor_name] = factor_train_data
            temp_factor_pool_test[factor_name] = factor_test_data
            utils.dump_json_factors(temp_factor_pool_train, file_pattern)
            utils.dump_json_factors(temp_factor_pool_test, file_pattern_test)
        pass

    def validate_new_factors(self,new_factors_train,new_factors_test):
        assert new_factors_test.keys() == new_factors_train.keys()
        pass_factors_list = []
        error_insample=[]
        error_outsample=[]
        for factor_name in new_factors_train.keys():
            self.check_in_sample_performance(factor_name, new_factors_train[factor_name])
            self.check_in_sample_corr(factor_name, new_factors_train[factor_name])
            if sum(self.passed_factors[factor_name]) == 2:
                print(f"Factor {factor_name} passed In-sample tests")
                if self.run_out_of_sample(factor_name,new_factors_test[factor_name],target_on_test):
                    print(f"Factor {factor_name} passed Out-of-sample tests")
                    print(f"Factor {factor_name} passed all the tests, add to the factor pool")
                    pass_factors_list.append(factor_name)
                    self.enter_into_factor_pool(factor_name,new_factors_train[factor_name],new_factors_test[factor_name])
                else:
                    print(f"Factor {factor_name} failed Out-of-sample tests")
                    error_outsample.append(factor_name)
                    # utils.add_factor_to_OTS_test(factor_name=factor_name)
                # utils.add_factor_to_OTS_test(factor_name=factor_name)
            else:
                print(f"Factor {factor_name} failed in-sample tests")
                error_insample.append(factor_name)
            print('==============================================================================================================')
        print('\n')
        print('______________________________________Overall Conclusion________________________________________________________')
        print('passed factors: ',pass_factors_list)
        print('failed outsample factors: ',error_outsample)
        print('failed insample factors: ',error_insample)
