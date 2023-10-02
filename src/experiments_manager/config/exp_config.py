from abc import ABC, abstractmethod

from ..path_manager import PathManager
from ..utils import utils_dict as utils_dict
from ..utils import utils_files as utils_files


class ExpConfig(ABC):
    
    ID_EXT = ".json"
    STRUCTURE = []
    MODULES_CONNECTOR = {}

    @classmethod
    def _set_paths(cls):
        cls.IDS     = PathManager.IDS_PATH + "/exp_config"
        cls.MODULES = PathManager.CONFIG_MODULES_PATH + "/exp_config"
    
    def __init__(self, raw_exp_config_dict:dict, path=None, id=None):
        ExpConfig._set_paths()
        if path is not None:
            self.init_from_path(path)
        elif id is not None:
            self.init_from_id(id)
        else:
            self.standard_init(raw_exp_config_dict)
    

    def init_from_path(self, path:str):
        self.exp_config_dict = utils_files.load_json_file(file_path=path)
        self.assign_attributes(self.exp_config_dict)
        self.id = path.split("/")[-1].split(".")[0]
        self.structure_path = self.build_structure_path()
    

    def init_from_id(self, id: str):
        pass
    

    def standard_init(self, raw_exp_config_dict:dict):
        self.exp_config_dict = self.preprocess_config(raw_exp_config_dict)
        self.assign_attributes(self.exp_config_dict)
        self.id, is_new = self.assign_id()
        self.structure_path = self.build_structure_path()
        if is_new: self.save_exp_config(id)
        

    def preprocess_config(self, raw_exp_config):
        return raw_exp_config
    

    def build_structure_path(self):
        return self.id
    
    
    def assign_id(self):
        hash = utils_dict.dict2hash(self.exp_config_dict)
        id = "exp_"+hash
        other_ids = utils_files.find_all_json_files_in_dir(ExpConfig.IDS, with_ext=False)
        is_new = (id not in other_ids)
        return id, is_new
    

    def assign_attributes(self, input_dict, distinction:str=None):
        for key, value in input_dict.items():
            if isinstance(value, dict):
                setattr(self, key, value)
                self.assign_attributes(value, distinction=key)
            else:
                if hasattr(self, key):
                    key = distinction+"_"+key
                    if hasattr(self, key):
                        raise Exception(f"Attribute '{key}' already exists!")
                setattr(self, key, value)
        
    
    def save_exp_config(self, id):
        file_path = self.get_id_path()
        utils_files.save_json_dict_to_path(file_path, self.exp_config_dict)

    def get_id_path(self):
        return ExpConfig.IDS+"/"+self.structure_path + ExpConfig.ID_EXT

    def get_structure_path(self):
        return self.structure_path
    
    def get_id(self):
        return self.id
    
    def pretty_print(self):
        utils_dict.print_dict_pretty(self.exp_config_dict)

    
    def __getitem__(self, name):
        return self.__dict__.get(name, None)

    def __contains__(self, item):
        return item in self.__dict__
    
    def get(self, key, default=None):
        if key in self:  # This uses the __contains__ method
            return self[key]  # This uses the __getitem__ method
        else:
            return default