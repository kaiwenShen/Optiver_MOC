'''
This script will serve as the framework for factors testing. The helper methods will be added on demand. One can use this for in-sample fitting and testing, and
we will use this for out-of-sample testing.

existed_factors: A dictionary stored all the passed factors, with key being the names of the factors and values being the factor values in np.ndarray
testing_factors: A dictionary stored all the factors waited for the testing, with the same format of existed_factors
factor_performance: A dictionary stored all the existed factors' performance score (in-sample correlation with target value)
'''
import numpy as np
# import utils
from time import time
import json
target_on_train = np.load('./out_of_sample/target_on_train.npy')
target_on_train[np.isnan(target_on_train)] = 0
# target_on_test = np.load('./factor_design_ver2_beta/target_on_test.npy')
# target_all = np.load('./factor_design_ver2_beta/target_all.npy')
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
        corr_coef = np.corrcoef(factor_value, target_on_train)[0,1]
        self.passed_factors[factor_name] = []
        self.factor_performance[factor_name] = corr_coef
        if corr_coef > corr_coef_threshold:
            # this factor pass this step
            print(f"Factor {factor_name} passed in-sample performance check with correlation coefficient {corr_coef}")
            self.passed_factors[factor_name].append(1)
        else:
            print(f"Factor {factor_name} failed in-sample performance check with correlation coefficient {corr_coef}")
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
        corr_factors = {}
        threshold_1 = 0.4
        threshold_2 = 0.7
        performance_threshold_1 = 1.2
        performance_threshold_2 = 1.4
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
                    print(f"Factor {factor_name} failed in-sample correlation check with factor {old_factor_name}")
                    print(f"Factor {factor_name} has correlation coefficient {corr_coef} with factor {old_factor_name}, and so"\
                            f"we need the new factor performance to be at least {performance_threshold_1} times the old factor performance.")
                    print(f"Factor {factor_name} has in-sample performance {self.factor_performance[factor_name]} while "\
                            f"factor {old_factor_name} has in-sample performance {self.factor_performance[old_factor_name]}. The new factor {factor_name} is"\
                            f"not exceeding is not exceeding {performance_threshold_1} times the old factor {old_factor_name}'s performance.")
                    return None
            else:
                # need further check
                if self.factor_performance[factor_name] > performance_threshold_2 * self.factor_performance[old_factor_name]:
                    # pass for this existed factor
                    continue
                else:
                    self.passed_factors[factor_name].append(0)
                    print(f"Factor {factor_name} failed in-sample correlation check with factor {old_factor_name}")
                    print(f"Factor {factor_name} has correlation coefficient {corr_coef} with factor {old_factor_name}, and so"\
                            f"we need the new factor performance to be at least {performance_threshold_2} times the old factor performance.")
                    print(f"Factor {factor_name} has in-sample performance {self.factor_performance[factor_name]} while "\
                            f"factor {old_factor_name} has in-sample performance {self.factor_performance[old_factor_name]}, the new factor {factor_name} "\
                            f"performance is not exceeding {performance_threshold_2} times the old factor {old_factor_name }'s performance.")
                    return None
        # this new factor pass for all existed factors check
        self.passed_factors[factor_name].append(1)
        print(f"Factor {factor_name} passed in-sample correlation check with all existed factors")
        print(f"Factor {factor_name} has in-sample performance with all existed factors as below:")
        print(json.dumps(corr_factors[factor_name], indent=4))
    
    def run_testing(self):
        '''
        We will check the factor performance followed by the above three steps
        '''
        pass_factors_list = []
        failed_factors_list = []
        for factor_name, factor_value in self.testing_factors.items():
            print(f"Start testing factor: {factor_name}..........")
            self.check_in_sample_performance(factor_name, factor_value)
            self.check_in_sample_corr(factor_name, factor_value)
            if sum(self.passed_factors[factor_name]) == 2:
                print(f"Factor {factor_name} passed all the tests, and will be added to the factors for out-of-sample testing")
                # utils.add_factor_to_OTS_test(factor_name=factor_name)
                pass_factors_list.append(factor_name)
            else:
                failed_factors_list.append(factor_name)
                print(f"Factor {factor_name} failed one of the tests, and will not be added to the factors for out-of-sample testing")
        print(f"Factors passed all the tests: {pass_factors_list}")
        print(f"Factors failed at least one of the tests: {failed_factors_list}")


    def run_out_of_sample(self,factor_name,factor_data, target_data):
        out_of_sample_corr = np.corrcoef(factor_data, target_data)[0,1]
        print(f"Out of sample correlation coefficient for factor {factor_name} is {out_of_sample_corr}")
        if out_of_sample_corr >= 0.05 or out_of_sample_corr >=0.7*self.factor_performance[factor_name]:
            print(f"Factor {factor_name} passed out-of-sample performance \n in-sample corr = {self.factor_performance[factor_name]} \n out-of-sample corr = {out_of_sample_corr}")
            print('True')

