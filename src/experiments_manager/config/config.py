import os
from abc import ABC, abstractmethod

import utils.utils_dict as utils_dict
import utils.utils_files as utils_files

from hyperparams import Hyperparams
from expConfig import ExpConfig
from extraConfig import ExtraConfig
from ..paths import Paths


class Config(ABC):

    RESULTS_STRUCTURE = ["exp_config", "hyperparams"]
    RESULTS_FILES_EXT = ""

    def __init__(self, hyperparams:Hyperparams, expConfig:ExpConfig, extraConfig:ExtraConfig):
        
        self.hyperparams = hyperparams
        self.expConfig   = expConfig
        self.extraConfig = extraConfig

        self.build_special_attr()
        
        self.results_folder_path = self.build_results_folder_path()
        self.config_results, self._is_complete = self.search_existing_results()
        if self.config_results is None: self.create_results_folder()
    

    def build_special_attr(self):
        pass
    

    def check_complete_results(self, result, verbose=False):
        if len(result)==0:
            if verbose: self.display_did_not_found_results(error_msg="is empty.")
            return False
        if verbose: self.display_found_existing_results()
        return True

    def new_trial(self):
        trial_params = {}
        return trial_params
    
    def display_config_infos(self, extra_space=True, max_infos=False):
        pass
    
    
    def create_results_folder(self):
        utils_files.create_folder(self.results_folder_path)


    def search_existing_results(self, verbose=False):
        if verbose: self.display_config_infos()
        if not os.path.isdir(self.results_folder_path):
            if verbose: self.display_did_not_found_results(error_msg="doesn't exist.")
            return None, False
        raw_results_dict = Config.build_results_dict(self.results_folder_path)
        is_complete = self.check_complete_results(raw_results_dict)
        return raw_results_dict, is_complete
    

    def build_results_folder_path(self):
        structures_paths_dict = {"hyperparams":self.hyperparams.get_structure_path(), "exp_config":self.expConfig.get_structure_path()}
        path_list = [ structures_paths_dict[key] for key in Config.RESULTS_STRUCTURE ]
        structure_path = "/".join(path_list)
        results_folder_path = Paths.RESULTS +"/"+ structure_path
        return results_folder_path
    

    @staticmethod
    def build_results_dict(directory):
        results = {}
        for filename in os.listdir(directory):
            if filename.endswith(Config.RESULTS_FILES_EXT):
                if Config.RESULTS_FILES_EXT==".pkl":
                    results[filename] = utils_files.load_pickle_file(os.path.join(directory, filename))
        return results


    def display_found_existing_results(self):
        print("  ==> Found results at:"+self.unique_results_folder_path)
    
    def display_did_not_found_results(self, error_msg):
        print("  --> No results were found for this config: path '"+self.results_folder_path+"' "+error_msg)
    
    def is_complete(self):
        return self._is_complete

    
    