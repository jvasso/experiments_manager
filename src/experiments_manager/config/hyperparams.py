from abc import ABC, abstractmethod

import utils.utils_dict as utils_dict
import utils.utils_files as utils_files

from paths import Paths

class Hyperparams(ABC):

    IDS = Paths.IDS + "/hyperparams"
    IDS_EXT = ".json"
    STRUCTURE = []

    def __init__(self, hyperparams_dict:dict=None, id:str=None):
        if (id is not None) and (hyperparams_dict is not None):
            self.easy_init(hyperparams_dict, id)
        elif (id is not None):
            self.init_from_id(id)
        else:
            assert id is None
            self.standard_init(hyperparams_dict)
        
        self.load_special_attributes()
    

    def easy_init(self, definitive_hyperparams_dict: dict, id: str):
        self.hyperparams_dict = definitive_hyperparams_dict
        self.assign_attributes(self.hyperparams_dict)
        self.id = id
        self.structure_path = self.build_structure_path()
        self.infos_dict = "not provided (easy init)"
        
    
    def init_from_id(self, id):
        file_path = Hyperparams.IDS+"/"+id+".json"
        self.hyperparams_dict = utils_files.load_json_file(file_path)
        self.assign_attributes(self.hyperparams_dict)
        self.id = id
        self.structure_path = self.build_structure_path()
        self.infos_dict = "not provided (init_from_id)"

    def standard_init(self, raw_hyperparams_dict:dict):
        self.hyperparams_dict, self.infos_dict = self.preprocess_hyperparams(raw_hyperparams_dict)
        self.id, self.is_new = Hyperparams.assign_id(self.hyperparams_dict)
        self.structure_path = self.build_structure_path()
        self.assign_attributes(self.hyperparams_dict)


    def preprocess_hyperparams(self, raw_hyperparams_dict):
        return raw_hyperparams_dict, {}
    
    def load_special_attributes(self):
        pass

    def build_structure_path(self):
        return self.id

    
    def assign_attributes(self, input_dict, distinction:str=None):
        for key, value in input_dict.items():
            if isinstance(value, dict):
                self.assign_attributes(value, distinction=key)
            else:
                if hasattr(self, key):
                    key = distinction+"_"+key
                    if hasattr(self, key):
                        raise Exception(f"Attribute '{key}' already exists!")
                setattr(self, key, value)
    

    @staticmethod
    def assign_id(hyperparams_dict):
        hash = utils_dict.dict2hash(hyperparams_dict)
        id = "hyp_"+hash
        other_ids = utils_files.get_json_filenames(Hyperparams.IDS, with_ext=False)
        is_new = (id not in other_ids)
        if is_new: Hyperparams.save_hyperparams(id, hyperparams_dict)
        return id
    
    @staticmethod
    def save_hyperparams(id, hyperparams_dict):
        file_path = Hyperparams.IDS + "/"+ id + ".json"
        utils_files.save_json_dict_to_path(file_path, hyperparams_dict)
    
    
    @staticmethod
    def check_leaves(d):
        if not isinstance(d, dict):
            return False
        if not d:
            return True
        for k, v in d.items():
            if isinstance(v, list):
                return False
            elif isinstance(v, dict):
                return Hyperparams.check_leaves(v)
        return True
    

    def get_structure_path(self):
        return self.structure_path
    
    def get_dict(self):
        return self.hyperparams_dict

    def get_id(self):
        return self.id
    
    def get_id_path(self):
        return Hyperparams.IDS+"/"+self.structure_path + Hyperparams.IDS_EXT
    
    def print_pretty(self):
        utils_dict.print_dict_pretty(self.hyperparams_dict)