from abc import ABC, abstractmethod
import time

from ..config import Config


class Experiment(ABC):
    
    def __init__(self, config):
        assert type(config)==Config
        self.config = config
    

    def _run_exp(self, save_results=True, verbose=False):
        start_time = time.time()
        while not self.config.is_complete():
            trial_params = self.config.new_trial()
            results = self.run_exp(trial_params)
            assert self.check_format(results)
            if save_results: self.config.save_trial_result(results, trial_params)
        end_time = time.time()
        running_time = end_time-start_time
        infos = {"running_time":running_time}
        if verbose:print("\nTook "+str(end_time-start_time)+" seconds.")
    

    @abstractmethod
    def run_exp(self, trial_params=None):
        pass

    
    def check_format(self, result):
        mandatory_metrics = self.config.extra_config.metrics
        recorded_metrics = result.keys()
        for mandatory_metric in mandatory_metrics :
            if mandatory_metric not in recorded_metrics:
                return False
        return True