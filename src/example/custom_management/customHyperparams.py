from experiments_manager.config import Hyperparams


class CustomHyperparams(Hyperparams):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)