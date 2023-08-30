
from experiments_manager.config import Config
from experiments_manager.experiment import Trial

import random


class CustomExperiment(Trial):

    def __init__(self, config:Config, seed):
        super().__init__(config)
        self.seed = seed


    def _run_experiment(self):
        
        random.seed(a=self.seed)
        result = random.randint(0,9)

        return result