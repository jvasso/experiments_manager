from abc import ABC, abstractmethod

from ..path_manager import PathManager
from ..utils import utils_dict as utils_dict
from ..utils import utils_files as utils_files

import pprint

class BaseConfig(ABC):

    @classmethod
    def _set_paths(cls, name, ids=True):
        cls.MODULES_TAG = "config_module"
        cls.COMMON_MODULES = PathManager.CONFIG_MODULES_PATH + "/common"
        cls.MODULES_CONNECTOR = {}
        cls.INTERNAL_CONNECTOR = {}
        cls.IDS_EXT = ".json"
        if ids: cls.IDS = PathManager.IDS_PATH + "/" + name
        cls.MODULES = PathManager.CONFIG_MODULES_PATH + "/" + name
    
    @classmethod
    def _set_special_paths(cls):
        pass
    
    def __init__(self, name:str, prefix:str, assign_id:bool=True, assign_attributes:bool=False):
        type(self)._set_paths(name, assign_id)
        type(self)._set_special_paths()
        self.name   = name
        self.prefix = prefix
        self._assign_id = assign_id
        self._assign_attributes = assign_attributes
    

    def standard_init(self, raw_config_dict:dict):
        self.config_dict, self.infos_dict = self.preprocess_config_dict(raw_config_dict)
        if self._assign_id:
            self._id = self.assign_id(self.config_dict, self.prefix)
            self._structure_path = self.build_structure_path()
        if self._assign_attributes: self.assign_attributes(self.config_dict)
    

    def init_from_id(self, id):
        file_path = type(self).IDS+"/"+id+type(self).IDS_EXT
        self.config_dict = utils_files.load_json_file(file_path)
        if self._assign_attributes: self.assign_attributes(self.config_dict)
        self._id = id
        self._structure_path = self.build_structure_path()
        self.infos_dict = "not provided (init_from_id)"
    

    def build_structure_path(self):
        return self._id
    
    
    def preprocess_config_dict(self, config_dict):
        config_dict = self.connect_modules(config_dict)
        config_dict = self.connect_tagged_modules(config_dict)
        config_dict = self.connect_internally(config_dict)
        return config_dict, {}
    

    def connect_modules(self, config_dict):
        modules_connector = type(self).MODULES_CONNECTOR
        for input_dict_path, output_os_path in modules_connector.items():
            utils_dict.connect_dict_to_file(input_dict_path, output_os_path, config_dict)
        return config_dict
    

    def connect_internally(self, config_dict):
        internal_connector = type(self).INTERNAL_CONNECTOR
        for input_dict_path, output_dict_path in internal_connector.items():
            utils_dict.connect_dict_internally(input_dict_path, output_dict_path, config_dict)
        return config_dict
    
    
    def connect_tagged_modules(self, raw_dict):
        remaining_modules = self.find_config_module(raw_dict, path="", parent=None, results=None)
        for triplet in remaining_modules:
            path, parent, super_parent, value = triplet["path"], triplet["parent"], triplet["super_parent"], triplet["value"]
            if path in type(self).MODULES_CONNECTOR.keys():
                raise NotImplementedError("TODO.")
            else:
                input_dict_path = path + "/" + type(self).MODULES_TAG
                modules = utils_files.get_dirnames_in_dir(type(self).MODULES)
                common_modules = utils_files.get_dirnames_in_dir(type(self).COMMON_MODULES)
                found_module = False
                for x in [parent, super_parent]:
                    if   x in modules:
                        output_os_path  = type(self).MODULES + path.split(x)[0] + x
                        found_module = True
                    elif x in common_modules:
                        output_os_path  = type(self).COMMON_MODULES + path.split(x)[0] + x
                        found_module = True
                if not found_module:
                    raise Exception(f"Module {path}/{value} not supported.")
                try:
                    utils_dict.connect_dict_to_file(input_dict_path=input_dict_path, output_os_path=output_os_path, data_dict=raw_dict, remove_key=type(self).MODULES_TAG)
                except:
                    raise Exception(f"Unable to connect dict path '{input_dict_path+'/'+value}' to os path '{output_os_path}'.\nHere's the dict:\n{pprint.pformat(raw_dict)}")
        return raw_dict
    


    def find_config_module(self, tree, path="", parent=None, super_parent=None, results=None):
        if results is None:
            results = []
        for key, value in tree.items():
            new_path = path + "/" + key
            if key == type(self).MODULES_TAG:
                results.append({
                    'path': path,
                    'parent': parent,
                    'super_parent': super_parent,
                    'value': value
                })
            if isinstance(value, dict):
                self.find_config_module(tree=value, path=new_path, parent=key, super_parent=parent, results=results)
        return results
    
    
    def assign_attributes(self, input_dict:dict, distinction:str=None):
        for key, value in input_dict.items():
            if isinstance(value, dict):
                setattr(self, key, value)
                self.assign_attributes(value, distinction=key)
            else:
                is_property = False
                if hasattr(self, key):
                    is_property = (getattr(self, key, None) != property)
                    if not is_property:
                        key = distinction+"_"+key
                        if hasattr(self, key):
                            raise Exception(f"Attribute '{key}' already exists!")
                if not is_property:
                    setattr(self, key, value)
    

    def assign_id(self, config_dict:dict, prefix:str=""):
        hash = utils_dict.dict2hash(config_dict)
        id = prefix+"_"+hash
        other_ids = utils_files.get_json_filenames(type(self).IDS, with_ext=False)
        is_new = (id not in other_ids)
        if is_new: self.save_config_dict(id, config_dict)
        return id
    

    def save_config_dict(self, id, config_dict):
        file_path = type(self).IDS + "/"+ id + ".json"
        utils_files.save_json_dict_to_path(file_path, config_dict)
    

    def print_pretty(self):
        utils_dict.print_dict_pretty(self.config_dict)
    

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
                return BaseConfig.check_leaves(v)
        return True
    

    # def __getitem__(self, name):
    #     return self.__dict__.get(name, None)
    
    def __getitem__(self, name):
        return utils_dict.get_value_at_path(name, self.config_dict)
    
    def __contains__(self, item):
        return item in self.config_dict
    
    def get(self, key, default=None):
        if key in self:  # This uses the __contains__ method
            return self[key]  # This uses the __getitem__ method
        else:
            return default
    

    @property
    def id(self):
        if self._assign_id:
            return self._id
        else:
            raise Exception(f"Object of class {type(self)} doesn't have an id.")
    
    @property
    def id_path(self):
        if self._assign_id:
            return type(self).IDS+"/"+self._structure_path + type(self).IDS_EXT
        else:
            raise Exception(f"Object of class {type(self)} doesn't have an id.")
    
    @property
    def structure_path(self):
        if self._assign_id:
            return self._structure_path
        else:
            raise Exception(f"Object of class {type(self)} doesn't have a structure_path.")
        
