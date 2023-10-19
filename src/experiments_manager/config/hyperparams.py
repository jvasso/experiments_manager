from .base_config import BaseConfig

from ..utils import utils_dict as utils_dict
from ..utils import utils_files as utils_files


class Hyperparams(BaseConfig):
    
    def __init__(self, config_dict:dict=None, id:str=None, assign_attributes:bool=True):
        super().__init__(name="hyperparams", prefix="hyp", assign_id=True, assign_attributes=assign_attributes)
        
        if (id is not None) and (config_dict is not None):
            self.easy_init(config_dict, id)
        elif (id is not None):
            self.init_from_id(id)
        else:
            assert id is None
            self.standard_init(config_dict)
    

    def easy_init(self, definitive_config_dict: dict, id: str):
        self.config_dict = definitive_config_dict
        if self._assign_attributes: self.assign_attributes(self.config_dict)
        self._id = id
        self._structure_path = self.build_structure_path()
        self.infos_dict = "not provided (easy init)"
    

    def build_structure_path(self):
        return self._id