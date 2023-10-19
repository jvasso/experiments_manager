
from ...experiments_manager.config import Config
from ...experiments_manager.experiment import Experiment

import random


class CustomExperiment(Experiment):

    def __init__(self, config:Config):
        super().__init__(config)
    

    def run_exp(self, trial_params):
        
        # hyperparams
        self.num_layers = self.config.hyperparams.num_layers
        self.activation = self.config.hyperparams.activation
        self.pretrained_model = self.config.hyperparams.pretrained_model
        
        # exp_config
        self.env_name = self.config.exp_config.env
        self.reward_name = self.config.exp_config.reward

        # extra_config
        self.log_frequency = self.config.extra_config.log_frequency
        
        random.seed(a=int(trial_params["seed"]))
        result = {"last_train_reward":random.randint(0,9), "last_test_reward":random.randint(0,9)}
        model = "random"
        
        return result, model