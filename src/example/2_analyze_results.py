import pprint

from custom_management.customConfigManager import CustomConfigManager
from custom_management.customHyperparams import CustomHyperparams
from custom_management.customExpConfig import CustomExpConfig
from custom_management.customExtraConfig import CustomExtraConfig
from custom_management.customConfig import CustomConfig
from custom_management.customResultsManager import CustomResultsManager
from custom_management.customExpResults import CustomExpResults

criteria = CustomExpResults.LAST_TRAIN_REWARD


configManager = CustomConfigManager(hyperparams_cls=CustomHyperparams,
                                    expConfig_cls=CustomExpConfig,
                                    extraConfig_cls=CustomExtraConfig,
                                    config_cls=CustomConfig)
resultsManager = CustomResultsManager(configManager=configManager)
infos = resultsManager.rank_according_to_criteria(criteria, verbose=True)

mean_scores_per_corpus, rank_per_corpus, ranking_details, global_ranking = infos["mean_scores_per_corpus"], infos["rank_per_corpus"], infos["ranking_details"], infos["global_ranking"]

print("\Scores per corpus:")
pprint.pprint(mean_scores_per_corpus)

print("\nRanking details:")
pprint.pprint(ranking_details)

print("\nGLOBAL RANKING:")
pprint.pprint(global_ranking)

save_report_response = input("Save report?\n")
if save_report_response in {"y","Y","yes","YES"}:
    resultsManager.save_report()