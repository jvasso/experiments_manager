from .base_config import BaseConfig

from ..utils import utils_dict as utils_dict



class ExtraConfig(BaseConfig):

    SAVE_RESULTS_KEY = "save_results"
    SAVE_MODEL_KEY = "save_model"

    def __init__(self, config_dict:dict, assign_attributes:bool=True):
        super().__init__(name="extra_config", prefix="extra", assign_id=False, assign_attributes=assign_attributes)
        
        self.standard_init(config_dict)
    