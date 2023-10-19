from .base_config import BaseConfig

from ..utils import utils_dict as utils_dict
from ..utils import utils_files as utils_files


class ExpConfig(BaseConfig):

    def __init__(self, config_dict:dict, path=None, id=None, assign_attributes:bool=True):
        super().__init__(name="exp_config", prefix="exp", assign_id=True, assign_attributes=assign_attributes)

        if path is not None:
            self.init_from_path(path)
        elif id is not None:
            self.init_from_id(id)
        else:
            assert id is None
            self.standard_init(config_dict)
    

    def init_from_path(self, path:str):
        self.config_dict = utils_files.load_json_file(file_path=path)
        if self._assign_attributes: self.assign_attributes(self.config_dict)
        self._id = path.split("/")[-1].split(".")[0]
        self._structure_path = self.build_structure_path()
        
    
    def build_structure_path(self):
        return self._id