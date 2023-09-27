from abc import ABC, abstractmethod
import time

from ..config import Config
from ..config import ExtraConfig

class Experiment(ABC):
    
    def __init__(self, config:Config):
        assert type(config)==Config
        self.config = config

        if ExtraConfig.SAVE_RESULTS_KEY in self.config.extra_config.__dict__.keys():
            self._save_results = self.config.extra_config[ExtraConfig.SAVE_RESULTS_KEY]
        else:
            self._save_results = True
        
        if ExtraConfig.SAVE_MODEL_KEY in self.config.extra_config.__dict__.keys():
            self._save_model = self.config.extra_config[ExtraConfig.SAVE_MODEL_KEY]
        else:
            self._save_model = False
    
    
    def _run_exp(self, verbose=False):
        start_time = time.time()
        while not self.config.is_complete():
            trial_params = self.config.new_trial()
            results, model = self.run_exp(trial_params)
            assert self.check_format(results), "The dictionary 'results' does not follow the expected format:\n"+repr(results)+"\nExpected format:\n"+repr(self.config.extra_config.metrics)
            if self._save_results: self.config.save_trial_result(results, trial_params)
            if self._save_model: self.save_model(model, self.config.results_folder_path+"/model")
        end_time = time.time()
        running_time = end_time-start_time
        infos = {"running_time":running_time}
        if verbose:print("\nTook "+str(end_time-start_time)+" seconds.")
    

    @abstractmethod
    def run_exp(self, trial_params=None):
        pass
    
    def save_model(self, model, path):
        raise Exception("You must implement the save_model method to be able to save the model.")
    
    def load_model(self, path):
        raise Exception("You must implement the load_model method to be able to load a model.")

    
    def check_format(self, result):
        mandatory_metrics = self.config.extra_config.metrics
        recorded_metrics = result.keys()
        for mandatory_metric in mandatory_metrics :
            if mandatory_metric not in recorded_metrics:
                return False
        return True