import globals.PATHS as PATHS

from management.resultsManager import ResultsManager
from visualization.visualizer import Visualizer

import os
import pdb, traceback, sys

response2id = {"s":"25", "sd":"26", "r":"ruche", "25":"25", "26":"26", "ruche":"ruche"}

try:
    # get results folder dir
    is_results_from_remote = input("\nLoad remote results?\n")
    if is_results_from_remote in {"yes", "y", "YES", "Y"}:
        device_response = input("Which device? (25: 's', 26: 'sd', ruche: 'r')\n")
        assert device_response in response2id.keys()
        device_id = response2id[device_response]
        new_folder = input("Folder number: ")
        new_path = "./../../remote_results/"+device_id+"/new_results"+new_folder+"/code/"
        assert os.path.isdir(new_path)
        PATHS.SET_EXTRA_PATH(new_path)
    elif is_results_from_remote not in {"n", "no", "N", "NO"}:
        raise Exception("Invalid answer: "+str(is_results_from_remote))

    #hyperparams_ids_list = ['hyperparams22-12-28-21h05min13sec73782-7im', 'hyperparams22-12-28-21h05min13sec74043-KM2']
    selection="best_10"
    hyperparams_ids_dict, exp_params_ids_list, full_hyperparams_ids_list, hyperparam2mean_score, hyperparam2std_score = ResultsManager.follow_gridsearch_report(selection=selection)
    episodes_choice = "all"
    comparison_params = ["features_params", "heads", "lr", "gnn_arch"]
    #comparison_params = None
    final = False
    legend_mode="mode1"
    visualizer = Visualizer(hyperparams_ids_dict, exp_params_ids_list, comparison_params=comparison_params,
                            full_hyperparams_ids_list=full_hyperparams_ids_list,
                            hyperparam2mean_score=hyperparam2mean_score, hyperparam2std_score=hyperparam2std_score,
                            final=final)
    visualizer.plot_results(episodes_choice=episodes_choice,legend_mode=legend_mode)

except:
    extype, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)

