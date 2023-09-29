from genericpath import isfile
import os
import yaml
import json
import pickle
import datetime
import string
import secrets
import fnmatch


def load_yaml_file(filename):
    filename = filename+".yaml" if not (".yaml" in filename) else filename
    with open(filename) as f:
        cfg = yaml.load(f, Loader=yaml.Loader)
    return cfg


def load_json_file(file_path:str):
    if not file_path.endswith(".json"): file_path += ".json"
    if not os.path.isfile(file_path): return None
    with open(file_path, 'r') as json_file:
        data_dict = json.load(json_file)
    return data_dict


def load_pickle_file(file_path:str):
    if not file_path.endswith(".pkl"):
        file_path += ".pkl"
    if os.path.exists(file_path):
        with open(file_path, 'rb') as pickle_file:
            data_dict = pickle.load(pickle_file)
        return data_dict
    else:
        return None


def save_json_dict_to_path(path: str, data: dict):
    if not path.endswith(".json"):
        path += ".json"
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4)

def save_pickle_dict_to_path(path: str, data: dict, is_new=False):
    if path.endswith(".json"): raise Exception("Error: should not end with .json")
    if not os.path.exists(os.path.dirname(path)): os.makedirs(os.path.dirname(path))
    if not path.endswith(".pkl"): path += ".pkl"
    already_exists = os.path.exists(path)
    if is_new and already_exists :raise Exception("Error: the path '"+path+"' is not new, but should be.")
    with open(path, 'wb') as file:
        pickle.dump(data, file)


def load_json_filenames_from_dir(dir_path):
    files = os.listdir(dir_path) if os.path.isdir(dir_path) else []
    json_files = fnmatch.filter(files, "*.json")
    if len(json_files)==0:
        return None
    elif len(json_files) == 1:
        return json_files[0]
    else:
        raise Exception("Error: multiple files found in "+dir_path)

def search_pickle_in_dir(dir_path):
    files = os.listdir(dir_path) if os.path.isdir(dir_path) else []
    pickle_files = fnmatch.filter(files, "*.pkl")
    if len(pickle_files)==0:
        return None
    elif len(pickle_files) == 1:
        return pickle_files[0]
    else:
        raise Exception("Error: multiple files found in "+dir_path)


def maybe_create_folder(dir_path):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

def get_dirnames_in_dir(directory):
    return [f.name for f in os.scandir(directory) if f.is_dir()]

def get_filenames_in_dir(directory):
    return [f.name for f in os.scandir(directory) if f.is_file()]
    # return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def create_unique_date_id(key_length=4):    
    formatted_time = datetime.datetime.now().strftime("%y-%m-%d-%Hh%Mmin%Ssec%f")[:-1]
    unique_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(key_length))
    return formatted_time+"-"+unique_key

def find_most_recent(dates_list):
    return max(dates_list, key=lambda x: datetime.datetime.strptime(x, "%y-%m-%d-%Hh%Mmin%Ssec%f"))


def load_json_dicts_from_dir(dir_path):
    dumped_dict = {}
    filenames_list = get_json_filenames(dir_path)
    for filename in filenames_list:
        with open(dir_path+"/"+filename, 'r') as f:
            new_dict = json.load(f)
            new_dict_dumped = dump_dict(new_dict)
            dumped_dict[filename] = new_dict_dumped
    return dumped_dict


def dump_dict(dict):
    return json.dumps(dict, sort_keys=True)
    

def search_dict_in_dumps(target_dict, dumped_dicts):
    dumped_target_dict = json.dumps(target_dict, sort_keys=True)
    for filename, dumped_dict in dumped_dicts.items():
        if dumped_dict == dumped_target_dict:
            return filename
    return None


def get_json_filenames(directory, with_ext=True):
    filenames = []
    if os.path.isdir(directory):
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                if with_ext:
                    filenames.append(filename)
                else:
                    filenames.append(filename.split(".json")[0])
    return filenames


def find_all_json_files_in_dir(directory, with_ext=True):
    if not os.path.isdir(directory):
        return "Invalid directory path"
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                if with_ext: 
                    json_files.append(file)
                else:
                    json_files.append(file.split(".json")[0])
    return json_files


def get_yaml_filenames(directory):
    filenames = []
    if os.path.isdir(directory):
        for filename in os.listdir(directory):
            if filename.endswith(".yaml"):
                filenames.append(filename)
    return filenames


def list_of_lines2file(list_of_lines, file_path):
    with open(file_path, "w") as f:
        for line in list_of_lines:
            if not line.endswith("\n"): line += "\n"
            f.write(line)
    

def get_tree_structure(path):
    tree = {}
    for item in os.listdir(path):
        full_item_path = os.path.join(path, item)
        if os.path.isdir(full_item_path):
            tree[item] = get_tree_structure(full_item_path)
        else:
            tree[item] = None
    return tree


def find_files_in_dir(directory_path, filenames, remove_ext=True):
    found_files = []
    not_found_files = filenames.copy()
    for root, dirs, files in os.walk(directory_path):
        for idx in range(len(files)):
            file = files[idx] 
            if remove_ext: file = file.split(".")[0]
            if file in filenames:
                found_files.append(os.path.join(root, file))
                not_found_files.remove(file)
    return found_files, not_found_files

