from experiments_manager.config import ExpConfig


class CustomExpConfig(ExpConfig):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    