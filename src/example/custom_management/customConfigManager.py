from experiments_manager.config import ConfigManager


class CustomConfigManager(ConfigManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    