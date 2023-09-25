from typing import Type
import numpy as np

from .extraConfig import ExtraConfig

from ..utils import utils_dict as utils_dict
from ..utils import utils_files as utils_files

import string
from itertools import product


class ConfigResult:

    STRUCTURE = ["seed"]
    RESULT_EXT = ".json"

    EXTRACONFIG_CRITERIA_KEY = "gridsearch_metric"
    COMPLETE_CRITERIA = "criteria_complete_result"
    result_loader = {".json":utils_files.load_json_file, ".pkl":utils_files.load_pickle_file}
    result_saver  = {".json":utils_files.save_json_dict_to_path, ".pkl":utils_files.save_pickle_dict_to_path}

    def __init__(self, extra_config:Type[ExtraConfig], results_dir:str, id:str=None):
        self.extra_config = extra_config
        self.metric_of_interest = self.extra_config[ConfigResult.EXTRACONFIG_CRITERIA_KEY]
        self.results_dir_path = results_dir
        self.num_expected_trials = self.get_num_expected_trials()
        if id is None:
            self.standard_init()
        else:
            self.init_from_id(id)
        self.remaining_trial_params = self.search_remaining_trial_params()
    

    def standard_init(self):
        self.id = utils_files.create_unique_date_id(key_length=2)
        self.result_folder_path = self.results_dir_path + "/" + self.id
        self.result_file_path = self.result_folder_path + "/results" + ConfigResult.RESULT_EXT
        self._is_new   = True
        self._is_empty = True
        utils_files.create_folder(self.result_folder_path)
        self.initialize_results_file()
    

    def init_from_id(self, id):
        self.id = id
        self.result_folder_path = self.results_dir_path + "/" + self.id
        self.result_file_path = self.result_folder_path + "/results" + ConfigResult.RESULT_EXT
        
        result_dict = self.load_results()
        if result_dict is not None:
            self.metric2metric_id = result_dict["infos"]["metrics"]
            self.metric_id2metric = {value:key for key,value in self.metric2metric_id.items()}
            self._is_empty = True if self.metric_of_interest not in self.metric2metric_id.keys() else False
        else:
            result_dict = self.initialize_results_file()
    
    

    def initialize_results_file(self):
        results = {"infos":{"data_structure":ConfigResult.STRUCTURE, "metrics":self.extra_config["metrics"]}, "data":{}}
        utils_files.save_json_dict_to_path(self.result_file_path, results)
        self._is_new   = True
        self._is_empty = True
        self.metric2metric_id = results["infos"]["metrics"]
        self.metric_id2metric = {value:key for key,value in self.metric2metric_id.items()}
        return results

    
    def new_trial(self):
        return self.remaining_trial_params[0]
    
    
    def save_trial_results(self, new_result_dict, trial_params):
        results = self.load_results()
        data_structure = results["infos"]["data_structure"]
        metrics_dict = results["infos"]["metrics"]
        metrics_ids = metrics_dict.values()
        for metric in new_result_dict:
            if metric not in metrics_dict or (metrics_dict[metric] is None):
                new_metric_id = self.generate_metric_id(metric, metrics_ids)
                results["infos"]["metrics"][metric] = new_metric_id
        path = ["data"]+[ trial_params[key] for key in data_structure ]
        tiny_result_dict = { results["infos"]["metrics"][key]:new_result_dict[key] for key in new_result_dict.keys() }
        results = utils_dict.set_value_at_path(path, tiny_result_dict, results)
        ConfigResult.result_saver[ConfigResult.RESULT_EXT](self.result_file_path, results)
        self.remaining_trial_params.remove(trial_params)
    

    def generate_metric_id(self, metric, metrics_ids):
        alphabet = string.ascii_lowercase
        i = 1
        while True:
            for combination in product(alphabet, repeat=i):
                new_id = ''.join(combination)
                if new_id not in metrics_ids:
                    return new_id
            i += 1

    
    def load_results(self):
        return ConfigResult.result_loader[ConfigResult.RESULT_EXT](self.result_file_path)
    

    def search_remaining_trial_params(self):
        # if self._is_new or self._is_empty:
            # return self.generate_all_trial_params()
            # self.data_structure
        result_dict = self.load_results()
        self.metric_of_interest_id = self.metric2metric_id[self.metric_of_interest]
        self.data_structure = result_dict["infos"]["data_structure"]
        level_dict = result_dict["data"]
        remaining_trial_params = self.search_incomplete_results(level_dict, 0)
        return remaining_trial_params


    def search_incomplete_results(self, level_dict, key_idx):
        incomplete_level_keys = []
        key = self.data_structure[key_idx]
        expected_keys = self.generate_expected_keys(key)
        for expected_key in expected_keys:
            if key_idx == len(self.data_structure)-1:
                if self.is_incomplete(level_dict, expected_key):
                    incomplete_level_keys.append({key:expected_key})
            else:
                if (expected_key not in level_dict.keys()) or (level_dict[expected_key] is None):
                    level_dict[expected_key] = {}
                incomplete_level_subkeys = self.search_incomplete_results(level_dict[expected_key], key_idx+1)
                incomplete_level_keys = incomplete_level_keys + [ {**current_dict, key:expected_key} for current_dict in incomplete_level_subkeys ]
        return incomplete_level_keys
    

    def merge_accross_trials(self, trial_params="all", metrics="all", stats=["mean", "std"]):
        results = self.load_results()
        if metrics == "all":
            metrics = results["infos"]["metrics"]
        else:
            for metric in metrics: assert metric in results["infos"]["metrics"]
        metrics_ids = [self.metric2metric_id[metric] for metric in metrics]
        merged_results = { metric:[] for metric in metrics }
        results_stats = { metric:{} for metric in metrics }
        if trial_params=="all":
            for root, dirs, metric2val_list in utils_dict.walk_tree(results["data"]):
                if type(metric2val_list)==list:
                    for id2val_tuple in metric2val_list:
                        metric_id, val = id2val_tuple
                        if metric_id in metrics_ids:
                            merged_results[self.metric_id2metric[metric_id]].append(val)
        else:
            raise Exception("Not implemented.")
        for metric, vals_list in merged_results.items():
            results_stats[metric] = {stat_name: round(ConfigResult.stat_name2func(stat_name)(vals_list),3) for stat_name in stats}
        return merged_results, results_stats
    

    @staticmethod
    def stat_name2func(stat_name):
        stat_dict = {"mean":np.mean, "std":np.std}
        return stat_dict[stat_name]


    def is_incomplete(self, level_dict, expected_key):
        if expected_key not in level_dict.keys():
            return True
        elif type(level_dict[expected_key]) != dict:
            return True
        elif self.metric2metric_id[self.metric_of_interest] not in level_dict[expected_key].keys():
            return True
        return False

    
    def get_num_expected_trials(self):
        keys_values = [ len(self.generate_expected_keys(key)) for key in self.extra_config[ConfigResult.COMPLETE_CRITERIA].keys()]
        num_expected_trials = np.prod(keys_values)
        return num_expected_trials


    def generate_expected_keys(self, key):
        expected_num = self.extra_config[ConfigResult.COMPLETE_CRITERIA][key]
        expected_keys = [ str(num) for num in range(expected_num)]
        return expected_keys


    def generate_new(self, num:int, level="seed"):
        pass