from experiments_manager.results import ExpResults


class CustomExpResults(ExpResults):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)