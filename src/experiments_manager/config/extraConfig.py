
from ..paths import Paths
from ..utils import utils_dict as utils_dict


class ExtraConfig:

    MODULES_EXTRA_CONFIG = Paths.MODULES + "/extra_config"
    EXTRA_CONFIG_MODULES_CONNECTOR = {}

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