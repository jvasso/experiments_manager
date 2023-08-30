
from typing import Type

import time
from datetime import timedelta

from experiments_manager.config import Hyperparams

from utils.utils_dict import dict2hash

from ..config.configManager import ConfigManager
from experiment import Trial


class ExperimentManager:

    def __init__(self, configManager:ConfigManager, experiment_cls:Type[Trial]):
        
        self.configManager = configManager
        self.experiment_cls = experiment_cls
        self.configs_to_run = self.configManager.get_configs_to_do()
    
    
    def run_experiments(self, hyperparam_optimizer=None, num_trials=100, verbose=True):

        if hyperparam_optimizer is not None:
            self.optimize_hyperparams(hyperparam_optimizer, num_trials=num_trials)
        else:
            self.exp_infos_list = []
            start_time = time.time()
            for idx in range(len(self.configs_to_run)) :
                config = self.configs_to_run[idx]
                if verbose:print("\nCONFIG "+str(idx+1)+"/"+str(len(self.configs_to_run))+"\n")
                if verbose:config.display_config_infos(extra_space=False, max_infos=True)
                experiment = self.experiment_cls(config)
                results, exp_infos = experiment.run()
                self.exp_infos_list.append(exp_infos)            
            end_time = time.time()
            
            total_time = timedelta(seconds=end_time - start_time)
            if verbose:print(len(self.configs_to_run), "configurations tested in", total_time)
    
    
    def optimize_hyperparams(self, optimizer, num_trials=100, verbose=True):
        self.configManager.prepare_hyperparam_optim()
        search_space = self.preprocess_search_space(self.configManager.hyperparam_search_space)
        for expConfig in self.configManager.expConfigs_list:
            # config = self.configManager.get_config(expConfig, hyperparams)
            expConfig_id = expConfig.id
            configs_done = self.configManager.expConfig2configDone[expConfig]
            previous_results = self.get_hyperparams_results_pairs(configs_done)
            self.initialize_optimizer(optimizer, previous_results)
            for trial_idx in range(num_trials):
                reduced_hyperparam_dict = self.get_suggestion(optimizer, search_space)
                reduced_hyperparam_hash = dict2hash(reduced_hyperparam_dict)
                hyperparam_id = self.configManager.reduced_hash2hyperparam_id[reduced_hyperparam_hash]
                config = self.configManager.get_config(hyperparam_id=hyperparam_id, expConfig_id=expConfig_id)
                experiment = self.experiment_cls(config)
                results, exp_infos = experiment.run()
                
                
            
    
    def preprocess_search_space(self, search_space):
        return search_space

    def args2params(self):
        pass


    def objective(self, args):
         hyperparam = self.configManager.args2hyperparam(args)
         config = self.configManager.get_config()
         results, exp_infos = experiment.run()