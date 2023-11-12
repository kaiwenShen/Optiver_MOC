'''
This script will serve as the framework for factors testing. The helper methods will be added on demand. One can use this for in-sample fitting and testing, and
we will use this for out-of-sample testing.

existed_factors: A dictionary stored all the passed factors, with key being the names of the factors and values being the factor values in np.ndarray
testing_factors: A dictionary stored all the factors waited for the testing, with the same format of existed_factors
factor_performance: A dictionary stored all the existed factors' performance score (in-sample correlation with target value)
'''
import numpy as np
from . import utils
import pprint
import json
target_on_train = np.load('./factor_design_distributed_ver1/target_on_train.npy')
target_on_train[np.isnan(target_on_train)] = 0
class Factor_Backtest:
    def __init__(self, existed_factors: dict, testing_factors: dict, factor_performance: dict):
        self.existed_factors = existed_factors
        self.testing_factors = testing_factors
        self.factor_performance = factor_performance
        self.passed_factors = {}

    def check_in_sample_performance(self, factor_name: str, factor_value: np.ndarray):
        '''
        The new factor should perform in-sample with Pearson correlation coefficient > 0.05 with target value
        '''
        corr_coef_threshold = 0.05
        corr_coef = np.corrcoef(factor_value, target_on_train)[0,1]
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
                if self.factor_performance[factor_name] > corr_coef * performance_threshold_1 * self.factor_performance[old_factor_name]:
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
                if self.factor_performance[factor_name] > performance_threshold_2 * self.factor_performance[old_factor_name]:
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
        print(f"Factor {factor_name} PASSED in-sample pairwise correlation check with all existed factors")
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
            print(f"\nStart testing factor: {factor_name}..........")
            print('==============================================================================================================')
            self.check_in_sample_performance(factor_name, factor_value)
            self.check_in_sample_corr(factor_name, factor_value)
            print('\n_______________________________________Factor Conclusion_______________________________________________________')
            if sum(self.passed_factors[factor_name]) == 2:
                print(f"Factor {factor_name} PASSED")
                utils.add_factor_to_OTS_test(factor_name=factor_name)
                pass_factors_list.append(factor_name)
            else:
                failed_factors_list.append(factor_name)
                print(f"Factor {factor_name} FAILED")
            print('==============================================================================================================')
        print('\n')
        print('______________________________________Overall Conclusion________________________________________________________')
        print(f"Factors passed all the tests: {pass_factors_list}")
        print(f"Factors failed at least one of the tests: {failed_factors_list}")

