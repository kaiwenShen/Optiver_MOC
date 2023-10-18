'''
This script will serve as the framework for factors testing. The helper methods will be added on demand. One can use this for in-sample fitting and testing, and
we will use this for out-of-sample testing.

existed_factors: A dictionary stored all the passed factors, with key being the names of the factors and values being the factor values in np.ndarray
testing_factors: A dictionary stored all the factors waited for the testing, with the same format of existed_factors
factor_performance: A dictionary stored all the existed factors' performance score (in-sample correlation with target value)
'''
import numpy as np
from . import utils
import os
target_on_train = np.load('./factor_design_ver2_beta/target_on_train.npy')
target_on_test = np.load('./factor_design_ver2_beta/target_on_test.npy')
target_all = np.load('./factor_design_ver2_beta/target_all.npy')
class Factor_Backtest:
    def __init__(self, existed_factors: dict, testing_factors: dict, factor_performance: dict):
        self.existed_factors = existed_factors
        self.testing_factors = testing_factors
        self.factor_performance = factor_performance
        self.passed_factors = {}

    def check_in_sample_performance(self):
        '''
        The new factor should perform in-sample with Pearson correlation coefficient > ? 
        ?: set 0.4 for an example now, change later based on EDA results
        '''
        for factor_name, factor_value in self.testing_factors.items():
            corr_coef = np.corrcoef(factor_value, target_on_train)[0,0]
            # corr_coef = np.corrcoef(factor_value, target_on_train)
            # print(corr_coef)
            self.passed_factors[f"{factor_name}_train"] = []
            self.factor_performance[f"{factor_name}_train"] = corr_coef
            if corr_coef > 0.4:
                # this factor pass this results
                self.passed_factors[f"{factor_name}_train"].append(1)
            else:
                self.passed_factors[f"{factor_name}_train"].append(0)
                print(f"Factor {factor_name} failed in-sample performance test with corr_coef {corr_coef}")


    def check_in_sample_corr(self):
        '''
        For each testing factor, we examine whether it has a correlation coefficient:
        1. Less than 0.4 with all of the existed factors: the testing factor passed
        2. Between 0.4 and 0.7 with some existed factor: the in-sample performance of the new factor
        needs to be better than (1?)x the in-sample performance of this old factor
        3. Larger than 0.7 with some existed factor: the in-sample performance of the new factor
        needs to be better than 1.2x the in-sample performance of this old factor
        '''
        for factor_name, factor_value in self.testing_factors.items():
            for factor_name_, factor_value_ in self.existed_factors.items():
                corr_coef = np.corrcoef(factor_value, factor_value_)[0,1]
                if corr_coef < 0.4:
                    # pass directly
                    self.passed_factors[f"{factor_name}_train"].append(1)
                elif 0.4 <= corr_coef < 0.7:
                    # need further check
                    if self.factor_performance[f"{factor_name}_train"] > self.factor_performance[f"{factor_name_}_train"]:
                        self.passed_factors[f"{factor_name}_train"].append(1)
                    else:
                        self.passed_factors[f"{factor_name}_train"].append(0)
                        continue
                else:
                    # need further check
                    if self.factor_performance[f"{factor_name}_train"] > 1.2 * self.factor_performance[f"{factor_name_}_train"]:
                        self.passed_factors[f"{factor_name}_train"].append(1)
                    else:
                        self.passed_factors[f"{factor_name}_train"].append(0)
                        continue

    # NEED TO discuss how to handle test train values       

    def check_out_sample_performance(self):
        '''
        The new factor should not decay more than 30% in out-of-sample performance compared to in-sample performance
        For researchers, one wouldn't need to use this function
        '''
        # This may need another dictionary to save factor values for testing factors on test set
        for factor_name in self.testing_factors.keys():
            if 0.7 * self.factor_performance[f"{factor_name}_train"] < self.factor_performance[f"{factor_name}_test"]:
                self.passed_factors[factor_name].append(1)
            else:
                self.passed_factors[factor_name].append(0)
    
    def run_testing(self,train_test_type):
        '''
        We will check the factor performance followed by the above three steps
        '''
        self.check_in_sample_performance()
        self.check_in_sample_corr()
        # self.check_out_sample_performance()
        for factor_name, factor_value in self.testing_factors.items():
            if sum(self.passed_factors[f"{factor_name}_{train_test_type}"]) == 2:
                utils.add_factor_to_existed(factor_name=factor_name, factor_value=factor_value, test_type="train")
                print("xiaban ")
            else:
                print("!xiaban ")
                print(self.passed_factors)
                continue