from experiments_manager.config import ConfigManager
from experiments_manager.experiment import ExperimentManager

from custom_management.customExperiment import CustomExperiment


configManager = ConfigManager()
experimentManager = ExperimentManager(configManager, experiment_cls=CustomExperiment)
experimentManager.run_experiments()


