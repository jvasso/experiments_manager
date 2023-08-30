from abc import ABC, abstractmethod
import time

from ..config import Config


class Trial(ABC):
    
    def __init__(self, config):
        assert type(config)==Config
        self.config = config
        self.trial_params = self.config.new_trial()
    
    def save_results(self):
        pass
    
    def run(self, verbose=False):
        start_time = time.time()
        results = self._run_experiment()
        end_time = time.time()
        running_time = end_time-start_time
        infos = {"running_time":running_time}
        if verbose:print("\nTook "+str(end_time-start_time)+" seconds.")
        return results, infos
    
    
    @abstractmethod
    def _run_experiment(self):
        pass