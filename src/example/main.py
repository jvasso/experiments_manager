from ..experiments_manager.config import ConfigManager
from .. experiments_manager.experiment import ExperimentManager

from .custom_management.customExperiment import CustomExperiment



project_path = "."
configManager = ConfigManager(project_path=project_path, verbose_level=2)
experimentManager = ExperimentManager(configManager, experiment_cls=CustomExperiment, verbose=2)
experimentManager.run_experiments()


