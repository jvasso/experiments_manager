from experiments_manager.config import Config


class CustomConfig(Config):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build_special_attr(self):
        self.special_attr = 0
    