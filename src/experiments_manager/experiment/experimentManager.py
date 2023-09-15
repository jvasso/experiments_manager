
from typing import Type, List

import time
from datetime import timedelta

from ..config import Config
from ..config import ConfigManager
from .experiment import Experiment

from ..utils import utils_dict as utils_dict


class ExperimentManager:

    def __init__(self, configManager:ConfigManager, experiment_cls:Type[Experiment], verbose_level=0):
        self.configManager = configManager
        self.experiment_cls = experiment_cls
        self.configManager.partially_completed_configs
        self.verbose = verbose_level
    
    
    def run_experiments(self, hyperparam_optimizer=None, num_trials:int=None):
        if self.verbose>=1: print("\nRUNNING EXPERIMENTS")
        if hyperparam_optimizer is not None:
            raise Exception("not implemented")
            self.optimize_hyperparams(hyperparam_optimizer, num_trials=num_trials)
        else:
            self.num_configs = len(self.configManager.partially_completed_configs)+len(self.configManager.incomplete_configs)
            start_time = time.time()

            if self.verbose>=2: print("\nRunning partiallly completed configs")
            self.run_configs(self.configManager.partially_completed_configs, save_results=True)
            
            if self.verbose>=2: print("\nRunning new configs")
            self.run_configs(self.configManager.incomplete_configs, save_results=True)

            end_time = time.time()
            total_time = timedelta(seconds=end_time - start_time)
            if self.verbose>=1: print("\n"+str(self.num_configs)+ " configs executed in "+str(total_time))


    def run_configs(self, configs_list:List[Config], save_results=True, verbose=False):
        num_configs = len(configs_list)
        for idx in range(num_configs):
            config = configs_list[idx]
            if self.verbose >= 2: print("• Config "+str(idx+1)+"/"+str(num_configs))
            if self.verbose >= 3: config.display_config_infos()
            experiment = self.experiment_cls(config)
            experiment._run_exp(save_results=save_results)
    
    
    def optimize_hyperparams(self, optimizer, num_trials=100, verbose=True):
        self.configManager.prepare_hyperparam_optim()
        search_space = self.preprocess_search_space(self.configManager.hyperparam_search_space)
        for exp_config in self.configManager.exp_config_list:
            # config = self.configManager.get_config(exp_config, hyperparams)
            exp_config_id = exp_config.id
            configs_done = self.configManager.exp_config2configDone[exp_config]
            previous_results = self.get_hyperparams_results_pairs(configs_done)
            self.initialize_optimizer(optimizer, previous_results)
            for trial_idx in range(num_trials):
                reduced_hyperparam_dict = self.get_suggestion(optimizer, search_space)
                reduced_hyperparam_hash = utils_dict.dict2hash(reduced_hyperparam_dict)
                hyperparam_id = self.configManager.reduced_hash2hyperparam_id[reduced_hyperparam_hash]
                config = self.configManager.get_config(hyperparam_id=hyperparam_id, exp_config_id=exp_config_id)
                experiment = self.experiment_cls(config)
                results, exp_infos = experiment._run_exp()
    
    
    def preprocess_search_space(self, search_space):
        return search_space


    # def objective(self, args):
    #      hyperparam = self.configManager.args2hyperparam(args)
    #      config = self.configManager.get_config()
    #      results, exp_infos = experiment.run()