
from ..utils import utils_dict as utils_dict
from ..path_manager import PathManager

class ExtraConfig:

    EXTRA_CONFIG_MODULES_CONNECTOR = {}
    SAVE_RESULTS_KEY = "save_results"
    SAVE_MODEL_KEY = "save_model"

    @classmethod
    def _set_paths(cls):
        cls.MODULES = PathManager.CONFIG_MODULES_PATH + "/extra_config"
    
    @classmethod
    def _set_special_paths(cls):
        pass

    def __init__(self, extra_config_dict:dict, assign_attributes:bool=True):
        self._assign_attributes = assign_attributes
        ExtraConfig._set_paths()
        type(self)._set_special_paths()
        self.extra_config_dict = ExtraConfig.preprocess_params(extra_config_dict)
        if self._assign_attributes: self.assign_attributes()
    

    def __getitem__(self, key):
        return self.extra_config_dict[key]
    
    
    @staticmethod
    def preprocess_params(raw_extra_config):
        # connect trainer and logger
        extra_config_connector = ExtraConfig.EXTRA_CONFIG_MODULES_CONNECTOR
        for input_dict_path, output_os_path in extra_config_connector.items():
            utils_dict.connect_dict_to_file(input_dict_path, output_os_path, raw_extra_config)
        return raw_extra_config
    

    def assign_attributes(self, distinction:str=None):
        for key, value in self.extra_config_dict.items():
            if hasattr(self, key):
                key = distinction+"_"+key
                if hasattr(self, key):
                    raise Exception(f"Attribute '{key}' already exists!")
            setattr(self, key, value)
    
    
    def __getitem__(self, name):
        return self.__dict__.get(name, None)
    
    def __contains__(self, item):
        return item in self.__dict__
    
    def get(self, key, default=None):
        if key in self:  # This uses the __contains__ method
            return self[key]  # This uses the __getitem__ method
        else:
            return default