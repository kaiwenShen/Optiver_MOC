'''
This script will serve as the framework for factors testing. The helper methods will be added on demand. One can use this for in-sample fitting and testing, and
we will use this for out-of-sample testing.

existed_factors: A dictionary stored all the passed factors, with key being the names of the factors and values being the factor values in np.ndarray
testing_factors: A dictionary stored all the factors waited for the testing, with the same format of existed_factors
factor_performance: A dictionary stored all the existed factors' performance score (in-sample correlation with target value)
'''
import numpy as np
from factor_design_ver2_beta import utils
from time import time
# import logging
target_on_train = np.load('./factor_design_ver2_beta/target_on_train.npy')
target_on_train[np.isnan(target_on_train)] = 0
# target_on_test = np.load('./factor_design_ver2_beta/target_on_test.npy')
# target_all = np.load('./factor_design_ver2_beta/target_all.npy')
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
        time_start = time()
        for factor_name, factor_value in self.testing_factors.items():
            corr_coef = np.corrcoef(factor_value, target_on_train)[0,1]
            self.passed_factors[factor_name] = []
            self.factor_performance[factor_name] = corr_coef
            if corr_coef > 0.4:
                # this factor pass this step
                print(f"Factor {factor_name} passed in-sample performance check with correlation coefficient {corr_coef}")
                self.passed_factors[factor_name].append(1)
            else:
                print(f"Factor {factor_name} failed in-sample performance check with correlation coefficient {corr_coef}")
                self.passed_factors[factor_name].append(0)
        time_end = time()
        '''
        Use logging to record the time used for this step. Also record the number of factors passed this step and 
        the correlation coefficient of each factor. 
        Write these information to a log file with name in_sample_performance.log. The log file will be cleared before each run
        '''
        # logging.basicConfig(filename='in_sample_performance.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)
        print(f"Time used for checking in-sample performance: {time_end - time_start} seconds")
        print(f"Number of factors passed this step: {utils.get_num_passed_factors(self.passed_factors)}")
        print(f"Correlation coefficient of each test factor: {utils.get_test_factors_performance(self.testing_factors, self.factor_performance)}")
        print(f"Factors passed this step: {[factor_name for factor_name in self.passed_factors.keys() if sum(self.passed_factors[factor_name]) == len(self.passed_factors[factor_name])]}")
        print(f"Factors failed this step: {[factor_name for factor_name in self.testing_factors.keys() if sum(self.passed_factors[factor_name]) != len(self.passed_factors[factor_name])]}")


    def check_in_sample_corr(self):
        '''
        For each testing factor, we examine whether it has a correlation coefficient:
        1. Less than 0.4 with all of the existed factors: the testing factor passed
        2. Between 0.4 and 0.7 with some existed factor: the in-sample performance of the new factor
        needs to be better than (1?)x the in-sample performance of this old factor
        3. Larger than 0.7 with some existed factor: the in-sample performance of the new factor
        needs to be better than 1.2x the in-sample performance of this old factor
        '''
        corr_factors = {}
        for factor_name, factor_value in self.testing_factors.items():
            corr_factors[factor_name] = {}
            for factor_name_, factor_value_ in self.existed_factors.items():
                corr_coef = np.corrcoef(factor_value, factor_value_)[0, 1]
                corr_factors[factor_name][factor_name_] = corr_coef
                if corr_coef < 0.4:
                    # pass directly for this existed factor
                    continue
                elif 0.4 <= corr_coef < 0.7:
                    # need further check
                    if self.factor_performance[factor_name] > self.factor_performance[factor_name_]:
                        # pass for this existed factor
                        continue
                    else:
                        self.passed_factors[factor_name].append(0)
                        print(f"Factor {factor_name} failed in-sample correlation check with factor {factor_name_}")
                        print(f"Factor {factor_name} has correlation coefficient {corr_coef} with factor {factor_name_}, and so"\
                              "we need the new factor performance to be at least 1 times the old factor performance.")
                        print(f"Factor {factor_name} has in-sample performance {self.factor_performance[factor_name]} while "\
                              "factor {factor_name_} has in-sample performance {self.factor_performance[factor_name_]}. The new factor {factor_name} is"\
                              "not exceeding the old factor {factor_name_}'s performance.")
                        return None
                else:
                    # need further check
                    if self.factor_performance[factor_name] > 1.15 * self.factor_performance[factor_name_]:
                        # pass for this existed factor
                        continue
                    else:
                        self.passed_factors[factor_name].append(0)
                        print(f"Factor {factor_name} failed in-sample correlation check with factor {factor_name_}")
                        print(f"Factor {factor_name} has correlation coefficient {corr_coef} with factor {factor_name_}, and so"\
                              "we need the new factor performance to be at least 1.2 times the old factor performance.")
                        print(f"Factor {factor_name} has in-sample performance {self.factor_performance[factor_name]} while "\
                              "factor {factor_name_} has in-sample performance {self.factor_performance[factor_name_]}, the new factor {factor_name} "\
                              "performance is not exceeding 1.2 times the old factor {factor_name_}'s performance.")
                        return None
            # this new factor pass for all existed factors check
            self.passed_factors[factor_name].append(1)
            print(f"Factor {factor_name} passed in-sample correlation check with all existed factors")
            print(f"Factor {factor_name} has in-sample performance {corr_factors[factor_name]} with all existed factors")
    
    def run_testing(self):
        '''
        We will check the factor performance followed by the above three steps
        '''
        self.check_in_sample_performance()
        self.check_in_sample_corr()
        # self.check_out_sample_performance()
        for factor_name, factor_value in self.testing_factors.items():
            if sum(self.passed_factors[factor_name]) == 2:
                print(f"Factor {factor_name} passed all the tests, and will be added to the factors for out-of-sample testing")
                utils.add_factor_to_OTS_test(factor_name=factor_name)
            else:
                print(f"Factor {factor_name} failed one of the tests, and will not be added to the factors for out-of-sample testing")


'''
The out-of-sample testing should not be accessed by researcher

def check_out_sample_performance(self):
        
        The new factor should not decay more than 30% in out-of-sample performance compared to in-sample performance
        For researchers, one wouldn't need to use this function
        
        # This may need another dictionary to save factor values for testing factors on test set
        for factor_name in self.testing_factors.keys():
            if 0.7 * self.factor_performance[factor_name] < self.factor_performance[f"{factor_name}_test"]:
                self.passed_factors[factor_name].append(1)
            else:
                self.passed_factors[factor_name].append(0)
'''
