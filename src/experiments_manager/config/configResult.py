from typing import Type

from extraConfig import ExtraConfig
import utils.utils_files as utils_files
import utils.utils_dict as utils_dict
from .config import Config


class ConfigResult:

    STRUCTURE = ["seed"]
    RESULT_EXT = ".json"
    EXTRACONFIG_CRITERIA_KEY = "gridsearch_metric"
    COMPLETE_CRITERIA = "criteria_complete_result"
    result_loader = {".json":utils_files.load_json_file, ".pkl":utils_files.load_pickle_file}

    def __init__(self, extraConfig:Type[ExtraConfig], path:str=None):
    
        self.extraConfig = extraConfig
        self.criteria = self.extraConfig[ConfigResult.EXTRACONFIG_CRITERIA_KEY]
        if path is None:
            self.id = utils_files.create_unique_date_id(key_length=2)
        else:
            self.init_from_path(path)


    def init_from_path(self, dir_path):
        self.id = dir_path["/"][-1]
        result_dict_path = dir_path + "results" + ConfigResult.RESULT_EXT
        self.result_dict = self.load_result(result_dict_path)
        self.extraConfig
        remaining_trial_params = self.analyze_results()
    


    def load_result(self, path):
        return ConfigResult.result_loader[ConfigResult.RESULT_EXT](path)
    

    def analyze_results(self):
        metric_of_interest = self.extraConfig[ConfigResult.EXTRACONFIG_CRITERIA_KEY]
        metric2metric_id = self.result_dict["infos"]["metrics"]
        if metric_of_interest not in metric2metric_id.keys():
            return None
        level_dict = self.result_dict
        data_structure = self.result_dict["infos"]["data_structure"]
        for key_idx in range(len(data_structure)):
            key = data_structure[key_idx]
            expected_num = self.extraConfig[ConfigResult.COMPLETE_CRITERIA][key]
            num = len(level_dict)
            if num < expected_num:
                new_num = self.generate_new()
            if key_idx < 
            level_dict = 


    def generate_new(self, num:int, level="seed"):
        pass
    

    def check_complete_level(level_key="seed"):
        pass


    @staticmethod
    def build_id():
        return 