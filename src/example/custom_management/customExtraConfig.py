
from experiments_manager.config import ExtraConfig


class CustomExtraConfig(ExtraConfig):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
