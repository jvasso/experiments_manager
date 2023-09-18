from ..experiments_manager.config import ConfigManager
from .. experiments_manager.experiment import ExperimentManager

from .custom_management.customExperiment import CustomExperiment

from .. experiments_manager.utils.utils_dict import pretty_print_dict

project_path = "."
configManager = ConfigManager(project_path=project_path, verbose_level=2)
experimentManager = ExperimentManager(configManager, experiment_cls=CustomExperiment, verbose_level=2)
experimentManager.run_experiments()

results = experimentManager.compare_results(metrics=["last_train_reward"])
pretty_print_dict(results)