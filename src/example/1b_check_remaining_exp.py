from custom_management.customConfigManager import CustomConfigManager
from custom_management.customHyperparams import CustomHyperparams
from custom_management.customExpConfig import CustomExpConfig
from custom_management.customExtraConfig import CustomExtraConfig
from custom_management.customConfig import CustomConfig

configManager = CustomConfigManager(hyperparams_cls=CustomHyperparams,
                                    expConfig_cls=CustomExpConfig,
                                    extraConfig_cls=CustomExtraConfig,
                                    config_cls=CustomConfig)
configManager.print_report()