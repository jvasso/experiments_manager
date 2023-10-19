import os
from abc import ABC, abstractmethod

from ..utils import utils_dict as utils_dict
from ..utils import utils_files as utils_files

from ..path_manager import PathManager
from .hyperparams import Hyperparams
from .exp_config import ExpConfig
from .extra_config import ExtraConfig
from .config_result import ConfigResult


class Config(ABC):

    RESULTS_FILES_EXT = ""
    STRUCTURE = ["exp_config", "hyperparams"]

    def __init__(self, hyperparams:Hyperparams, exp_config:ExpConfig, extra_config:ExtraConfig, verbose:int=0):
        
        self.hyperparams  = hyperparams
        self.exp_config   = exp_config
        self.extra_config = extra_config
        self.verbose = verbose
        
        self.results_folder_path = self.build_results_folder_path()
        self.config_result = self.search_existing_results()
    

    def display_config_infos(self):
        pass
    
    
    def save_trial_result(self, new_result, trial_params):
        self.config_result.save_trial_results(new_result, trial_params)


    # Il y a des resultats qui auront été enregistres de maniere differente mais qui 
    # auront quand meme les donnees necessaires pour la gridsearch
    # --> ce n'est pas la meme chose de faire une gridsearch et de lancer un truc juste pour la courbe
    # selon quel critère considère-t-on qu'on a fini une expé ?
    # 1er cas : on veut faire une gridsearch : seul 1 critère compte
    # 2e cas  : 
    # dans un result, il y a : 
    # • le result dict
    # • les logs
    
    # def check_complete_results(self, result, verbose=False):
    #     if len(result)==0:
    #         if verbose: self.display_not_found_results(error_msg="is empty.")
    #         return False
    #     if verbose: self.display_found_existing_results()
    #     return True


    def new_trial(self):
        trial_params = self.config_result.new_trial()
        return trial_params
    

    def create_results_folder(self):
        utils_files.maybe_create_folder(self.results_folder_path)

    
    def search_existing_results(self):
        results_ids = utils_files.get_dirnames_in_dir(self.results_folder_path) if os.path.isdir(self.results_folder_path) else []
        if len(results_ids) == 0:
            config_result = ConfigResult(self.extra_config, results_dir=self.results_folder_path, id=None)
        else:
            most_recent_id = Config.find_most_recent(results_ids)
            config_result = ConfigResult(self.extra_config, results_dir=self.results_folder_path, id=most_recent_id)
        return config_result


    @staticmethod
    def find_most_recent(dates):
        return max(dates)


    def build_results_folder_path(self):
        structures_paths_dict = {"hyperparams":self.hyperparams._structure_path, "exp_config":self.exp_config._structure_path}
        path_list = [ structures_paths_dict[key] for key in Config.STRUCTURE ]
        structure_path = "/".join(path_list)
        results_folder_path = PathManager.RESULTS_PATH +"/"+ structure_path
        return results_folder_path
    

    @staticmethod
    def build_results_dict(directory):
        results = {}
        for filename in os.listdir(directory):
            if filename.endswith(Config.RESULTS_FILES_EXT):
                if Config.RESULTS_FILES_EXT==".pkl":
                    results[filename] = utils_files.load_pickle_file(os.path.join(directory, filename))
        return results
    

    def merge_trial_results(self, trial_params="all", metrics="all"):
        results, results_stats = self.config_result.merge_accross_trials(trial_params=trial_params, metrics=metrics)
        return results, results_stats
    

    def check_result_progress(self):
        expected_trial_params  = self.config_result.num_expected_trials
        remaining_trial_params = len(self.config_result.search_remaining_trial_params())
        return 1 - remaining_trial_params/expected_trial_params, remaining_trial_params


    def is_complete(self):
        is_complete = (len(self.config_result.remaining_trial_params)==0)
        return is_complete

    
    