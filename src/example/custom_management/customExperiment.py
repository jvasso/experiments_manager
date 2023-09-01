
from experiments_manager.config import Config
from experiments_manager.experiment import Experiment

import random


class CustomExperiment(Experiment):

    def __init__(self, config:Config, seed):
        super().__init__(config)
        self.seed = seed


    def _run_experiment(self):
        
        random.seed(a=self.seed)
        result = random.randint(0,9)

        return result