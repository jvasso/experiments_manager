
from .config_manager import ConfigManager
from ..utils import utils_dict as utils_dict


class ExtraConfig:

    MODULES = ConfigManager.CONFIG_MODULES_PATH + "/extra_config"
    EXTRA_CONFIG_MODULES_CONNECTOR = {}

    SAVE_RESULTS_KEY = "save_results"
    SAVE_MODEL_KEY = "save_model"

    def __init__(self, raw_extra_config):
        self.extra_config_dict = ExtraConfig.preprocess_params(raw_extra_config)
        self.assign_attributes()
    

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