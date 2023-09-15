from genericpath import isdir
import os
from typing import Type
import copy
import pprint

from .hyperparams import Hyperparams
from .expConfig import ExpConfig
from .extraConfig import ExtraConfig
from .config import Config

from ..utils import utils_dict as utils_dict
from ..utils import utils_files as utils_files


class ConfigManager:

    PARTIALLY_COMPLETE_THRESHOLD = 0.5
    
    def __init__(self,
                 project_path:str=".",
                 hyperparams_cls:Type[Hyperparams]=Hyperparams,
                 exp_config_cls:Type[ExpConfig]=ExpConfig,
                 extra_config_cls:Type[ExtraConfig]=ExtraConfig,
                 config_cls:Type[Config]=Config,
                 hyperparams_ids_list:list=None,
                 exp_config_ids_list:list=None,
                 verbose_level:int=0):
        ConfigManager._set_paths(project_path)
        self.verbose = verbose_level
        if self.verbose >= 1: print("\nINITIALIZE ConfigManager")
        if (hyperparams_ids_list is not None):
            if (exp_config_ids_list is not None):
                self.init_from_ids(hyperparams_ids_list, exp_config_ids_list)
            else:
                self.init_from_hyperparams_ids(hyperparams_ids_list, exp_config_cls)
        else:
            self.standard_init(hyperparams_cls, exp_config_cls, extra_config_cls, config_cls)

    
    def standard_init(self, hyperparams_cls, exp_config_cls, extra_config_cls, config_cls:Type[Config]=Config, verbose=False):
        self.hyperparams_ids_list = None
        raw_hyperparams, raw_exp_config, raw_extra_config = self.load_config()
        self.hyperparams_list = self.preprocess_hyperparams(raw_hyperparams, hyperparams_cls)
        self.exp_config_list  = self.preprocess_exp_config(raw_exp_config, exp_config_cls)
        self.extra_config     = self.preprocess_extra_config(raw_extra_config, extra_config_cls)
        
        self.completed_configs, self.partially_completed_configs, self.incomplete_configs = self.classify_configs(config_cls)
        self.num_configs = len(self.completed_configs)+len(self.partially_completed_configs)+len(self.incomplete_configs)
        self.hyperparams_ids_list = [ hyperparam.id for hyperparam in self.hyperparams_list ]
        if verbose: self.print_report()
    
    
    def init_from_hyperparams_ids(self, hyperparams_ids_list, exp_config_cls):
        self.hyperparams_ids_list = hyperparams_ids_list
        _, raw_exp_config, raw_extra_config = self.load_config()
        
        self.exp_config_list  = self.preprocess_exp_config(raw_exp_config, exp_config_cls)
        self.hyperparams_list = ConfigManager.load_hyperparams(self.hyperparams_ids_list)
        self.extra_config     = self.preprocess_extra_config(raw_extra_config)
    

    def init_from_ids(self, hyperparams_ids_list, exp_config_ids_list):
        self.exp_config_ids_list  = exp_config_ids_list
        self.hyperparams_ids_list = hyperparams_ids_list
        
        _, __, raw_extra_config = self.load_config(no_hyperparams=True)

        self.exp_config_list  = ConfigManager.load_exp_config(self.exp_config_ids_list)
        self.hyperparams_list = ConfigManager.load_hyperparams(self.hyperparams_ids_list)
        self.extra_config     = self.preprocess_extra_config(raw_extra_config)
    

    def prepare_hyperparam_optim(self):
        hyperparams_list_of_dicts = [ hyperparam_obj.hyperparams_dict for hyperparam_obj in self.hyperparams_list ]
        ConfigManager.check_homogeneus_structure(hyperparams_list_of_dicts)
        hyperparams_dict_of_lists = utils_dict.LD2DL(hyperparams_list_of_dicts)
        self.hyperparam_search_space = copy.deepcopy(hyperparams_dict_of_lists)
        utils_dict.prune_tree_single_leaves(self.hyperparam_search_space)
        self.target_keys_paths = utils_dict.extract_paths_from_dict(self.hyperparam_search_space)

        # pour chaque objet hyperparam : construire son tiny_hyperparam
        hyper_param_tiny = [ hyperparam.reduced_dict for hyperparam in self.hyperparam_id_list ]

        # choisi un hyperparam --> le trouver dans la liste


    @staticmethod
    def check_homogeneus_structure(hyperparams_list_of_dicts):
        same_structure, idx = utils_dict.check_same_structure(hyperparams_list_of_dicts)
        if not same_structure:
            pprint.pprint(hyperparams_list_of_dicts[0])
            print("")
            pprint.pprint(hyperparams_list_of_dicts[idx])
            raise Exception("Hyperparams must have identical structures when using smart hyperparameter search. But the above dicts (indices 0 and "+str(idx)+" do not.")


    @staticmethod
    def load_exp_config(exp_config_ids_list):
        exp_config_list = []
        exp_config_ids_path = ExpConfig.IDS
        exp_config_file_paths, not_found_files = utils_files.find_files_in_dir(exp_config_ids_path, exp_config_ids_list, remove_ext=True)
        if len(not_found_files) > 0: raise Exception("Some exp_config ids were not found:\n"+"\n".join(not_found_files))
        exp_config_list = [ ExpConfig(path=file_path) for file_path in exp_config_file_paths]
        return exp_config_list


    @staticmethod
    def load_hyperparams(hyperparams_ids_list):
        hyperparams_list = []
        for hyperparams_id in hyperparams_ids_list:
            hyperparams = Hyperparams(id=hyperparams_id)
            hyperparams_list.append(hyperparams)
        return hyperparams_list


    def preprocess_hyperparams(self, raw_hyperparams:dict, hyperparams_cls: Type[Hyperparams]):
        """
        Preprocess hyperparams, convert them into list of objects.
        """
        if self.verbose>=1: print("Preprocessing hyperparams...")
        hyperparams_listified_leaves = utils_dict.listify_leaves(raw_hyperparams)
        hyperparams_list_of_dicts    = utils_dict.DL2LD(hyperparams_listified_leaves)
        hyperparams_list_of_obj = []
        hyperparams_ids = set()
        for hyperparams_dict in hyperparams_list_of_dicts:
            hyperparam_obj = hyperparams_cls(hyperparams_dict=copy.deepcopy(hyperparams_dict)) # TODO: try with and without deepcopy
            hyperparam_id = hyperparam_obj.get_id()
            if hyperparam_id not in hyperparams_ids:
                hyperparams_ids.add(hyperparam_id)
                hyperparams_list_of_obj.append(hyperparam_obj)
        return hyperparams_list_of_obj


    def preprocess_exp_config(self, raw_exp_config, exp_config_cls:Type[ExpConfig]):
        if self.verbose>=1: print("Preprocessing experiment configs...")
        exp_config_listified_leaves = utils_dict.listify_leaves(raw_exp_config)
        exp_config_list_of_dicts    = utils_dict.DL2LD(exp_config_listified_leaves)
        exp_config_list_of_objects  = [ exp_config_cls(copy.deepcopy(exp_config_dict)) for exp_config_dict in exp_config_list_of_dicts ]
        return exp_config_list_of_objects
    

    def preprocess_extra_config(self, raw_extra_config, extra_config_cls:Type[ExtraConfig]):
        if self.verbose>=1: print("Preprocessing extra config...")
        extra_config = extra_config_cls(copy.deepcopy(raw_extra_config))
        return extra_config
    
    
    def classify_configs(self, config_cls:Type[Config]=Config):
        if self.verbose>=1: print("Classifying configurations...")
        completed_configs = []
        partially_completed_configs = []
        incomplete_configs = []
        num_configs = len(self.exp_config_list)*len(self.hyperparams_list)
        config_idx  = 0
        for exp_config in self.exp_config_list:
            for hyperparams in self.hyperparams_list:
                if self.verbose >= 2: print("• Config "+str(config_idx+1)+"/"+str(num_configs))
                config = config_cls(hyperparams=hyperparams, exp_config=exp_config, extra_config=self.extra_config, verbose=self.verbose)
                result_progress = config.check_result_progress()
                if result_progress == 1:
                    if self.verbose >= 2: print("Already completed.")
                    completed_configs.append(config)
                elif result_progress >= ConfigManager.PARTIALLY_COMPLETE_THRESHOLD:
                    if self.verbose >= 2: print("Partially completed.")
                    partially_completed_configs.append(config)
                else:
                    if self.verbose >= 2: print("Not completed.")
                    incomplete_configs.append(config)
                config_idx += 1
        return completed_configs, partially_completed_configs, incomplete_configs

    
    def load_config(self, no_hyperparams=False):
        hyperparams  = None if no_hyperparams else ConfigManager.get_hyperparams(ConfigManager.HYPERPARAMS_PATH)
        exp_config   = utils_files.load_yaml_file(ConfigManager.EXP_CONFIG_PATH)
        extra_config = utils_files.load_yaml_file(ConfigManager.EXTRA_CONFIG_PATH)
        return hyperparams, exp_config, extra_config


    @staticmethod
    def get_hyperparams(dir):
        if not os.path.isdir(dir):
            dir += ".yaml" if ".yaml" not in dir else ""
            if not os.path.isfile(dir): raise Exception(dir + " is not a directory nor a file.")
            return utils_files.load_yaml_file(dir)
        hyperparams = {}
        _, sub_dirs, files = next(os.walk(dir))
        for file in files:
            file_no_ext, ext = file.split(".")
            if ext == "yaml":
                hyperparams[file_no_ext] = utils_files.load_yaml_file(dir+"/"+file)
        for sub_dir in sub_dirs:
            hyperparams[sub_dir] = ConfigManager.get_hyperparams(dir+"/"+sub_dir)
        return hyperparams
    

    @classmethod
    def _set_paths(cls, project_path):
        cls.PROJECT_PATH      = project_path
        cls.CONFIG_PATH       = cls.PROJECT_PATH + "/config"
        cls.HYPERPARAMS_PATH  = cls.CONFIG_PATH  + "/hyperparams"
        cls.EXP_CONFIG_PATH   = cls.CONFIG_PATH  + "/exp_config"
        cls.EXTRA_CONFIG_PATH = cls.CONFIG_PATH  + "/extra_config"
    

    def print_report(self):
        print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Config Manager report:\n")
        print("• "+str(len(self.exp_config_ids_list)) + " experiment configs")
        print("• "+str(len(self.hyperparams_list)) + " hyperparameter configs")
        print("• "+str(len(self.num_configs)) + " configs ("+str(len(self.completed_configs)) + " completed, "+str(len(self.partially_completed_configs)) + " partially, "+str(len(self.incomplete_configs)) + " incomplete)")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")