from .utils import utils_files


class PathManager:

    def __init__(self):
        pass
    
    @classmethod
    def _configure_project(cls, project_path):
        cls.PROJECT_PATH        = project_path
        cls.CONFIG_PATH         = cls.PROJECT_PATH + "/config"
        cls.IDS_PATH            = cls.PROJECT_PATH + "/ids"
        cls.RESULTS_PATH        = cls.PROJECT_PATH + "/results"
        cls.CONFIG_MODULES_PATH = cls.PROJECT_PATH + "/config_modules"

        utils_files.maybe_create_folder(cls.IDS_PATH)
        utils_files.maybe_create_folder(cls.RESULTS_PATH)
        utils_files.maybe_create_folder(cls.CONFIG_MODULES_PATH)
        