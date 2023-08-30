
from ..paths import Paths
import utils.utils_dict as utils_dict


class ExtraConfig:

    MODULES_EXTRA_CONFIG = Paths.MODULES + "/extra_params"
    EXTRA_PARAMS_MODULES_CONNECTOR = {}

    def __init__(self, raw_extra_params):
        self.extra_params_dict = ExtraConfig.preprocess_params(raw_extra_params)
    
    
    @staticmethod
    def preprocess_params(raw_extra_params):
        # connect trainer and logger
        extra_params_connector = ExtraConfig.EXTRA_PARAMS_MODULES_CONNECTOR
        for input_dict_path, output_os_path in extra_params_connector.items():
            utils_dict.connect_dict_to_file(input_dict_path, output_os_path, raw_extra_params)
        return raw_extra_params