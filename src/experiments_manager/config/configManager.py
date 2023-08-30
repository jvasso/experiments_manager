import os
from typing import Type
import copy
import pprint

from hyperparams import Hyperparams
from expConfig import ExpConfig
from extraConfig import ExtraConfig
from .config import Config
from ..paths import Paths

import utils.utils_files as utils_files
import utils.utils_dict as utils_dict


class ConfigManager:
    
    CONFIG              = Paths.PROJECT_PATH+"/config"
    CONFIG_HYPERPARAMS  = CONFIG+"/hyperparams"
    CONFIG_EXP_CONFIG   = CONFIG+"/exp_config"
    CONFIG_EXTRA_PARAMS = CONFIG+"/extra_params"

    def __init__(self,
                 hyperparams_cls:Type[Hyperparams]=Hyperparams,
                 expConfig_cls:Type[ExpConfig]=ExpConfig,
                 extraConfig_cls:Type[ExtraConfig]=ExtraConfig,
                 config_cls:Type[Config]=Config,
                 hyperparams_ids_list:list=None,
                 exp_config_ids_list:list=None):
        if (hyperparams_ids_list is not None):
            if (exp_config_ids_list is not None):
                self.init_from_ids(hyperparams_ids_list, exp_config_ids_list)
            else:
                self.init_from_hyperparams_ids(hyperparams_ids_list, expConfig_cls)
        else:
            self.standard_init(hyperparams_cls, expConfig_cls, extraConfig_cls, config_cls)

    
    def standard_init(self, hyperparams_cls, expConfig_cls, extraConfig_cls, config_cls, verbose=False):
        self.hyperparams_ids_list = None
        raw_hyperparams, raw_exp_config, raw_extra_config = ConfigManager.load_config()
        
        # preprocess config
        self.hyperparams_list = self.preprocess_hyperparams(raw_hyperparams, hyperparams_cls)
        self.expConfigs_list = self.preprocess_exp_config(raw_exp_config, expConfig_cls)
        self.extraConfig = ConfigManager.preprocess_extra_config(raw_extra_config, extraConfig_cls)
        
        # remove configs already done
        self.configs_done, self.configs_to_do = self.classify_configs(config_cls)
        
        self.hyperparams_ids_list = [ hyperparam.id for hyperparam in self.hyperparams_list ]
        if verbose: self.print_report()
    
    def init_from_hyperparams_ids(self, hyperparams_ids_list, expConfig_cls):
        self.hyperparams_ids_list = hyperparams_ids_list
        _, raw_exp_config, raw_extra_params = ConfigManager.load_config()
        
        # self.exp_configs_list, self.seeds_list, self.corpus_list = ConfigManager.preprocess_exp_config(raw_exp_config)
        self.expConfigs_list  = self.preprocess_exp_config(raw_exp_config, expConfig_cls)
        self.hyperparams_list = ConfigManager.load_hyperparams(self.hyperparams_ids_list)
        self.extraConfig      = self.preprocess_extra_config(raw_extra_params)
    

    def init_from_ids(self, hyperparams_ids_list, exp_config_ids_list):
        self.exp_config_ids_list  = exp_config_ids_list
        self.hyperparams_ids_list = hyperparams_ids_list
        
        _, __, raw_extra_params = ConfigManager.load_config(no_hyperparams=True)

        self.expConfigs_list = ConfigManager.load_exp_config(self.exp_config_ids_list)
        # self.seeds_list  = sorted(seeds_list)
        # self.corpus_list = sorted(corpus_list)
        self.hyperparams_list     = ConfigManager.load_hyperparams(self.hyperparams_ids_list)
        self.extraConfig         = self.preprocess_extra_config(raw_extra_params)
    

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
    
    # @staticmethod
    # def build_exp_config_ids_dict():
    #     exp_config_ids_path = ExpConfig.IDS
    #     exp_config_ids_dict = utils_files.get_tree_structure(exp_config_ids_path)
    #     return exp_config_ids_dict


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
        hyperparams_listified_leaves = utils_dict.listify_leaves(raw_hyperparams)
        hyperparams_list_of_dicts    = utils_dict.DL2LD(hyperparams_listified_leaves)
        hyperparams_list_of_obj = []
        hyperparams_ids = {}
        for hyperparams_dict in hyperparams_list_of_dicts:
            hyperparam_obj = hyperparams_cls(hyperparams_dict=copy.deepcopy(hyperparams_dict)) # TODO: try with and without deepcopy
            hyperparam_id = hyperparam_obj.get_id()
            if hyperparam_id not in hyperparams_ids:
                hyperparams_ids.add(hyperparam_id)
                hyperparams_list_of_obj.append(hyperparam_obj)
        return hyperparams_list_of_obj

    # @staticmethod
    # def preprocess_exp_config(raw_exp_config):
    #     seeds_list  = ConfigManager.generate_seeds(mode=raw_exp_config["seed"])
    #     corpus_list = raw_exp_config["corpus"]
    #     raw_exp_config["seed"] = seeds_list

    #     exp_config_listified_leaves = utils_dict.listify_leaves(raw_exp_config)
    #     exp_config_list_of_dicts    = ConfigManager.DL2LD(exp_config_listified_leaves)
    #     exp_config_list_of_objects  = [ ExpConfig(copy.deepcopy(exp_config_dict)) for exp_config_dict in exp_config_list_of_dicts ]
    #     return exp_config_list_of_objects, seeds_list, corpus_list
    def preprocess_exp_config(self, raw_exp_config, expConfig_cls:Type[ExpConfig]):
        seeds_list  = ConfigManager.generate_seeds(mode=raw_exp_config["seed"])
        raw_exp_config["seed"] = seeds_list
        exp_config_listified_leaves = utils_dict.listify_leaves(raw_exp_config)
        exp_config_list_of_dicts    = utils_dict.DL2LD(exp_config_listified_leaves)
        exp_config_list_of_objects  = [ expConfig_cls(copy.deepcopy(exp_config_dict)) for exp_config_dict in exp_config_list_of_dicts ]
        return exp_config_list_of_objects

    @staticmethod
    def remove_duplicates(list_of_objects):
        ids_list = []
        duplicates = []
        final_list_of_objects = []
        for obj in list_of_objects:
            obj_id = obj.get_id()
            if obj_id not in ids_list:
                ids_list.append(obj_id)
                final_list_of_objects.append(obj)
            else:
                duplicates.append(obj_id)
        return final_list_of_objects, duplicates
    

    def preprocess_extra_config(self, raw_extra_params, extraConfig_cls:Type[ExtraConfig]):
        extraConfig = extraConfig_cls(copy.deepcopy(raw_extra_params))
        return extraConfig
    
    
    def classify_configs(self, config_cls:Type[Config]):
        config_done  = []
        config_to_do = []
        for exp_config in self.expConfigs_list:
            for hyperparams in self.hyperparams_list:
                # config = Config(hyperparams=hyperparams, exp_config=exp_configs, dynamic_params=dynamic_params, extra_params=self.extra_params)
                config = config_cls(hyperparams=hyperparams, expConfig=exp_config, extraConfig=self.extraConfig)
                
                if config._is_complete() is None:
                    config_to_do.append(config)
                else:
                    config_done.append(config)
        return config_done, config_to_do

    
    @staticmethod
    def load_config(no_hyperparams=False):
        hyperparams  = None if no_hyperparams else ConfigManager.get_hyperparams(ConfigManager.CONFIG_HYPERPARAMS)
        exp_config   = utils_files.load_yaml_file(ConfigManager.CONFIG_EXP_CONFIG)
        extra_config = utils_files.load_yaml_file(ConfigManager.CONFIG_EXTRA_PARAMS)
        return hyperparams, exp_config, extra_config


    @staticmethod
    def get_hyperparams(dir):
        hyperparams = {}
        _, sub_dirs, files = next(os.walk(dir))
        for file in files:
            file_no_ext, ext = file.split(".")
            if ext == "yaml":
                hyperparams[file_no_ext] = utils_files.load_yaml_file(dir+"/"+file)
        for sub_dir in sub_dirs:
            hyperparams[sub_dir] = ConfigManager.get_hyperparams(dir+"/"+sub_dir)
        return hyperparams
    

    def print_report(self):
        print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Config Manager report:\n")
        print("• "+str(len(self.hyperparams_list)) + " hyperparameters")
        print("• "+str(len(self.corpus_list))+" corpus")
        # print("• "+str(len(self.seeds_list))+" seeds")
        print("• "+str(len(self.configs_to_do))+"/"+str(len(self.configs_to_do)+len(self.configs_done))+ " configs to run")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    

    def get_config_lists(self):
        return self.configs_done, self.configs_to_do
    
    def get_configs_to_do(self):
        return self.configs_to_do
    
    def get_expConfigs_list(self):
        return self.expConfigs_list
    
    # def get_nb_seeds(self):
    #     return len(self.seeds_list)
    
    # def get_seeds_list(self):
    #     return self.seeds_list
    

    def get_hyperparams_ids_list(self):
        assert self.hyperparams_ids_list is not None
        return self.hyperparams_ids_list
    
    def get_extra_params(self):
        return self.extraConfig