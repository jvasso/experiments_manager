from typing import List
import os
from abc import ABC, abstractmethod
import numpy as np
import copy
import time
import pprint

from visualization.trajectoryVisualizer import TrajectoryVisualizer

import globals.PATHS as PATHS
import globals.GLOBAL_VAR as GLOBAL_VAR

from ..config.config import Config
from ..config.configManager import ConfigManager
from expResults import ExpResults
import rl_modules.RL_functions as RL_functions

import utils.utils_files as utils_files
import utils.utils_dict as utils_dict
import utils.utils_others as utils_others


class ResultsManager(ABC):

    def __init__(self, configManager:ConfigManager=None):
        
        self.configManager   = configManager
        self.exp_configs_list = self.configManager.exp_config_list
        self.extra_config     = self.configManager.extra_config
        
        self.report        = None
        self.ranking_infos = None
        self.saved         = False

        hyperparams_list = self.configManager.hyperparams_list
        self.hyperparams_ids_list = [ hyperparams.id for hyperparams in hyperparams_list ]
        self.expResults_list = [ ExpResults(exp_config, self.extra_config, hyperparams_list=hyperparams_list) for exp_config in self.exp_configs_list ]


    def save_report(self):
        if self.report is None: self.report = self.build_report()

        reports_path    = PATHS.GRIDSEARCH_REPORTS
        reports_remote_absolute_path = PATHS.GRIDSEARCH_REPORTS_REMOTE_ABSOLUTE_PATH
        date_id         = utils_files.create_unique_date_id()
        report_filename = "report"+date_id
        report_path     = reports_path+"/"+report_filename
        report_remote_absolute_path = reports_remote_absolute_path+"/"+report_filename
        
        utils_files.save_json_dict_to_path(report_path, self.report)
        self.report_path = report_path
        self.report_remote_absolute_path = report_remote_absolute_path
        self.saved = True


    def build_report(self):
        report = {}
        report["criteria"] = self.criteria
        report["ranking_infos"] = self.ranking_infos
        report["exp_params_ids"]            = [exp_params.get_id() for exp_params in self.exp_configs_list]
        report["exp_params_structure_path"] = [exp_params.get_structure_path() for exp_params in self.exp_configs_list]
        return report


    @staticmethod
    def follow_gridsearch_report(filename="last", selection="best_5"):
        if filename == "last":
            reports_path = PATHS.GRIDSEARCH_REPORTS
            filenames_list = utils_files.get_filenames_in_dir(reports_path)
            json_filenames_ids = [filename.split(".json")[0] for filename in filenames_list if filename.endswith(".json")]
            dates_plus_key_list = [filename.split("report")[1] for filename in json_filenames_ids]
            dates2keys_dict = {filename.rsplit("-", 1)[0] : filename.rsplit("-", 1)[1] for filename in dates_plus_key_list}
            most_recent_date = utils_files.find_most_recent(list(dates2keys_dict.keys()))
            report_filename = "report"+most_recent_date+"-"+dates2keys_dict[most_recent_date]+".json"
            print("\nVisualizing from report: "+report_filename)
        else:
            report_filename = filename
        
        file_path = PATHS.GRIDSEARCH_REPORTS + "/" + report_filename
        report_dict = utils_files.load_json_file(file_path)
        accepted_ranks = list(range(1,int(selection.split("_")[1])+1))
        hyperparams_ids_dict = {}
        for hyperparams_id, rank in report_dict["ranking_infos"]["global_ranking"].items():
            if rank in accepted_ranks:
                hyperparams_ids_dict[rank] = hyperparams_id
        exp_params_ids_list = report_dict["exp_params_ids"]
        full_hyperparams_ids_list = list(report_dict["ranking_infos"]["global_ranking"].keys())
        hyperparam2mean_score = report_dict["ranking_infos"]["global_mean_scores"]
        hyperparam2std_score  = report_dict["ranking_infos"]["global_std_scores"]
        return hyperparams_ids_dict, exp_params_ids_list, full_hyperparams_ids_list, hyperparam2mean_score, hyperparam2std_score
    


    def build_corpus2results_dict(self, epochs_select_criteria:str, seeds_merging_criteria_list):
        if type(seeds_merging_criteria_list) != list: seeds_merging_criteria_list = [seeds_merging_criteria_list]
        
        corpus2results_dict = {}
        accepted_hyperparams_dict = self.get_hyperparams_results(criteria=epochs_select_criteria, no_reject=True)
        #assert len(rejected_hyperparams_dict) == 0

        for corpus_name in self.corpus_list:
            corpus2results_dict[corpus_name] = {}
            for hyperparam_id, hyperparam_dict in accepted_hyperparams_dict.items():
                hyperparam_corpus_dict = hyperparam_dict[corpus_name]
                all_seeds_train_results_list = [seed_dict["train"] for seed, seed_dict in hyperparam_corpus_dict.items()]
                all_seeds_test_results_list  = [seed_dict["test"] for seed, seed_dict in hyperparam_corpus_dict.items()]
                merging_seeds_dict = {}
                merging_seeds_dict["train"] = utils_dict.LD2DL(all_seeds_train_results_list)
                merging_seeds_dict["test"]  = utils_dict.LD2DL(all_seeds_test_results_list)
                for result_type, result_type_dict in merging_seeds_dict.items():
                    for epoch in result_type_dict:
                        results_list  = copy.deepcopy(result_type_dict[epoch])
                        result_type_dict[epoch] = { criteria: ResultsManager.merge_according_to_criteria(criteria, results_list) for criteria in seeds_merging_criteria_list}
                corpus2results_dict[corpus_name][hyperparam_id] = merging_seeds_dict
        return corpus2results_dict


    @staticmethod
    def merge_according_to_criteria(criteria:str, results_list:list, round=2):
        if criteria == ResultsManager.MEAN_REW:
            return np.round(np.mean(results_list), 2)
        elif criteria == ResultsManager.STD_REW:
            return np.round(np.std(results_list) , 2)
        else:
            raise Exception("ERROR: merging criteria "+criteria+" not supported.")

    
    def _rank_according_to_criteria(self, criteria:str, merge_keys:List[str]):
        pass


    
    def rank_according_to_criteria(self, criteria:str, verbose=True):
        
        ranking_infos = {"mean_scores_per_corpus":None, "rank_per_corpus":None, "global_ranking":None, "ranking_details":None}
        
        accepted_hyperparams_dict = self.get_hyperparams_results(criteria, no_reject=True)
        
        # mean and std score for each hyperparam
        print("\nCompute mean and std score for each hyperparam")
        start = time.time()
        mean_score_per_corpus = {}
        std_score_per_corpus  = {}
        all_scores = {hyperparam:[] for hyperparam in accepted_hyperparams_dict}
        for corpus in self.corpus_list:
            print("   •"+corpus)
            mean_score_per_corpus[corpus] = {}
            std_score_per_corpus[corpus] = {}
            for hyperparam, hyperparam_dict in accepted_hyperparams_dict.items():
                all_seeds_results = [ seed_result for seed, seed_result in hyperparam_dict[corpus].items()]
                all_scores[hyperparam] = all_scores[hyperparam] + all_seeds_results
                mean_seed_result  = np.mean(all_seeds_results)
                std_seed_result   = np.std(all_seeds_results)
                mean_score_per_corpus[corpus][hyperparam] = mean_seed_result
                std_score_per_corpus[corpus][hyperparam]  = std_seed_result
        global_mean_scores = {hyperparam:np.mean(all_scores[hyperparam]) for hyperparam in accepted_hyperparams_dict}
        global_std_scores  = {hyperparam:np.std(all_scores[hyperparam]) for hyperparam in accepted_hyperparams_dict}
        
        ranking_infos["mean_scores_per_corpus"] = mean_score_per_corpus
        ranking_infos["std_scores_per_corpus"]  = std_score_per_corpus
        ranking_infos["global_mean_scores"] = global_mean_scores
        ranking_infos["global_std_scores"]  = global_std_scores
        end = time.time()
        print("Done in "+str(end-start), " seconds.")

        # ranking per corpus
        print("\nRank per corpus")
        start = time.time()
        rank_per_corpus = {corpus:ResultsManager.rank_scores(corpus_dict) for corpus, corpus_dict in mean_score_per_corpus.items()}
        ranking_infos["rank_per_corpus"] = rank_per_corpus
        end = time.time()
        hyperparams2ranks = {}
        for hyperparam in accepted_hyperparams_dict:
            hyperparams2ranks[hyperparam] = {}
            for corpus, corpus_dict in rank_per_corpus.items():
                rank = corpus_dict[hyperparam]
                hyperparams2ranks[hyperparam][corpus] = rank
        ranking_infos["ranking_details"] = hyperparams2ranks
        print("Done in "+str(end-start), " seconds.")
        
        # global ranking
        print("\nGlobal ranking")
        start = time.time()
        global_ranking = ResultsManager.rank_scores(global_mean_scores, reverse=True)
        ranking_infos["global_ranking"] = global_ranking
        end = time.time()
        print("Done in "+str(end-start), " seconds.")

        # for the report
        self.exp_params_structures_dict = exp_params_structures_dict
        self.ranking_infos              = ranking_infos
        self.criteria                   = criteria

        if verbose:
            print("\Scores per corpus:")
            pprint.pprint(ranking_infos["mean_scores_per_corpus"])
            print("\nRanking details:")
            pprint.pprint(ranking_infos["ranking_details"],)
            print("\nGLOBAL RANKING:")
            pprint.pprint(ranking_infos["global_ranking"])

        return ranking_infos
    

    @staticmethod
    def rank_scores(scores, reverse=True):
        print("   rank scores in one corpus")
        # Sort the scores in descending order
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=reverse)
        # Create a dictionary to store the ranks
        ranks = {}
        # Iterate through the sorted list of scores and add the ranks to the dictionary
        for i, (key, value) in enumerate(sorted_scores):
            ranks[key] = i + 1
        return ranks


    def _get_hyperparams_results(self, criteria:str, no_reject=False, verbose=True):
        accepted_hyperparams_dict = { id:{} for id in self.hyperparams_ids_list }
        rejected_hyperparams_dict = {}

        for expResult in self.expResults_list:
            hyperparams_results_dict = expResult.get_results_according_to_criteria(criteria, no_reject=no_reject) # {hyperparam_id: result}

            previous_hyperparams_ids = list(accepted_hyperparams_dict.keys())
            for hyperparams_id in previous_hyperparams_ids:
                if hyperparams_id not in hyperparams_results_dict.keys():
                    deleted_result = accepted_hyperparams_dict.pop(hyperparams_id, None)
                    rejected_hyperparams_dict[hyperparams_id] = deleted_result






    
    def get_hyperparams_results(self, criteria:str, no_reject=False, verbose=True):

        # accepted_hyperparams_dict = {hyperparams_id: corpus: seed: result}
        # hyperparams_results_dict = {hyperparams_id: result} --> pour cette expResult
        
        ### parcourir les expés et en tirer les hyperparams ids
        inital_ids_dict = self.expResults_list[0].get_hyperparams_ids_dict()
        for expResult in self.expResults_list:
            hyperparams_ids_dict = expResult.get_hyperparams_ids_dict()
            for hyperparam_id, hyperparam_dict in hyperparams_ids_dict.items():
                if hyperparam_id not in inital_ids_dict.keys(): inital_ids_dict[hyperparam_id] = hyperparam_dict
        accepted_hyperparams_dict = { id:{} for id in inital_ids_dict }
        rejected_hyperparams_dict = {}

        # select hyperparams that give complete results (= good nb of epochs) for each experiment (= 1 corpus, 1 seed)
        for expResult in self.expResults_list:
            corpus:str         = expResult.get_corpus_id()
            seed:str           = expResult.get_seed_id()
            exp_params_id: str = expResult.get_exp_params_id()
            hyperparams_results_dict = expResult.get_results_according_to_criteria(criteria, no_reject=no_reject) # {hyperparam_id: result}
            
            previously_accepted_hyperparams = list(accepted_hyperparams_dict.keys())
            # delete from accepted_hyperparams the hyperparams that were not tested on this expResult
            for hyperparams_id in previously_accepted_hyperparams:
                if hyperparams_id not in hyperparams_results_dict.keys():
                    deleted_result = accepted_hyperparams_dict.pop(hyperparams_id, None)
                    rejected_hyperparams_dict[hyperparams_id] = deleted_result
            
            # search among hyperparams_results_dict the hyperparams_id that were tested on previous expResults
            for hyperparams_id, result in hyperparams_results_dict.items():
                if hyperparams_id in accepted_hyperparams_dict.keys(): # we cannot compare hyperparams that are not tested under all conditions
                    if not corpus in accepted_hyperparams_dict[hyperparams_id].keys():
                        accepted_hyperparams_dict[hyperparams_id][corpus] = {seed:result}
                    else:
                        accepted_hyperparams_dict[hyperparams_id][corpus][seed] = result
                else:
                    deleted_result = accepted_hyperparams_dict.pop(hyperparams_id, None)
                    rejected_hyperparams_dict[hyperparams_id] = deleted_result

        copy_accepted_hyperparams_dict = copy.deepcopy(accepted_hyperparams_dict)
        for hyperparams_id, result in copy_accepted_hyperparams_dict.items():
            if result == {}:
                deleted_result = accepted_hyperparams_dict.pop(hyperparams_id, None)
                rejected_hyperparams_dict[hyperparams_id] = deleted_result
        
        if verbose: ResultsManager.display_accepted_rejected_hyperparams(accepted_hyperparams_dict, rejected_hyperparams_dict)
        
        assert self.check_results(accepted_hyperparams_dict)
        
        return accepted_hyperparams_dict
    

    @staticmethod
    def display_accepted_rejected_hyperparams(accepted_hyperparams_dict, rejected_hyperparams_dict):
        print("\n• Accepted hyperparams:")
        for hyperparams_id in accepted_hyperparams_dict:
            print(hyperparams_id)
        print("\n• Rejected hyperparams:")
        if len(rejected_hyperparams_dict) == 0: print("None")
        for hyperparams_id in rejected_hyperparams_dict:
            print(hyperparams_id)
        print("")


    @staticmethod
    def remove_hyperparams_id_from_paths_dict(paths_dict, hyperparams_id):
        exp_p_keys_to_check = list(paths_dict.keys())
        for exp_p_key in exp_p_keys_to_check:
            exp_p_dict = paths_dict[exp_p_key]
            if hyperparams_id in exp_p_dict: del exp_p_dict[hyperparams_id]
        return paths_dict
    

    def check_results(self, hyperparams_results):
        corpus_set = None
        seeds_set  = None
        for hyperparam, hyperparam_dict in hyperparams_results.items():
            if corpus_set is None: corpus_set = set(hyperparam_dict.keys())
            if set(hyperparam_dict.keys()) != corpus_set:
                print("hyperparams '", hyperparam, "' were tested on corpus",set(hyperparam_dict.keys()),"instead of", corpus_set, ".")
                return False
            for corpus, corpus_dict in hyperparam_dict.items():
                if seeds_set is None: seeds_set = set(corpus_dict.keys())
                if set(corpus_dict.keys()) != seeds_set:
                    print("hyperparams '", hyperparam, "' were tested on seeds",set(corpus_dict.keys()),"instead of", seeds_set, ".")
                    return False
        return True
    

    def get_nb_episodes(self):
        pass