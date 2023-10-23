import json
import hashlib
from itertools import product
from typing import List, Union
import copy

from . import utils_files


def get_value_at_path(path, tree:dict):
    # assert type(tree)==dict
    path = maybe_str_path2list_path(path)
    current_node = tree
    for element in path:
        if not isinstance(current_node, dict) or (element not in current_node):
            return None
        current_node = current_node[element]
    return current_node


def set_value_at_path(path, value, tree:dict, maybe_new_path:bool=True, new_path:bool=False):
    assert type(tree)==dict
    path = maybe_str_path2list_path(path)
    current_dict = tree
    for i in range(len(path)):
        full_key_str = str("/".join( [path[j] for j in range(i+1)] ))
        key = path[i]
        if key in current_dict:
            if i == len(path)-1:
                if new_path:
                    raise Exception("Error: the path '"+path+"' already exists in this dictionary.")
                current_dict[key] = value
            elif type(current_dict[key]) == dict:
                current_dict = current_dict[key]
            else:
                print("WARNING: Parameter "+full_key_str+" is neither a leaf nor a dict.")
                break
        elif new_path or maybe_new_path:
            if i == len(path)-1:
                current_dict[key] = value
            else:
                current_dict[key] = {}
        else:
            raise Exception("Error: Parameter '"+full_key_str+"' was not found in hyperparameters.")
    return tree


def maybe_str_path2list_path(path):
    if type(path) == str:
        return str_path2list_path(path)
    elif type(path) == list:
        return path
    else:
        raise Exception("path object must be a list or str")


def str_path2list_path(str_path:str):
    # cannot start with "/"
    if str_path.startswith("/"):
        str_path = str_path[1:]
    
    path = str_path.split("/")
    return path


def merge_disjointed_dicts(*dicts):
    # assert dictionaries do not have common keys
    common_keys = set(dicts[0].keys())
    for dict_ in dicts[1:]:
        common_keys &= set(dict_.keys())
    if len(common_keys)>0:
        raise Exception("This function can only merge disjointed dictionaries.")
    # merge
    merged_dict = {}
    for dict_ in dicts:
        merged_dict.update(dict_)
    return merged_dict


def LD2DL(LD):
    DL = {k: [dic[k] for dic in LD] for k in LD[0]}
    return DL

def connect_dict_to_file(input_dict_path:str, output_os_path:str, data_dict:dict, remove_key:str=None):
    target_filename = get_value_at_path(input_dict_path, data_dict)
    target_file_path = output_os_path + "/" + target_filename
    if target_filename == "none":
        target_dict = None
    else:
        target_dict = utils_files.load_yaml_file(target_file_path)
    #assert target_dict is not None
    if remove_key is not None:
        input_dict_path = input_dict_path.split('/'+remove_key)[0]
    set_value_at_path(input_dict_path, target_dict, data_dict)


def connect_dict_internally(input_dict_path:str, output_dict_path:str, data_dict:dict):
    target_filename = get_value_at_path(input_dict_path, data_dict)
    if target_filename is None:
        target_dict = None
    else:
        target_file_path = output_dict_path + "/" + target_filename
        target_dict = get_value_at_path(target_file_path, data_dict)
    set_value_at_path(output_dict_path, target_dict, data_dict)


def print_dict_pretty(data_dict:dict):
    pretty = json.dumps(data_dict, indent=5)
    print(pretty)


def remove_duplicates(tree_dict):
    for key in tree_dict:
        if isinstance(tree_dict[key], list):
            tree_dict[key] = list(set(tree_dict[key]))
        elif isinstance(tree_dict[key], dict):
            remove_duplicates(tree_dict[key])


def customized_dumps(tree_dict, indent=4):
    def tree_to_json(d, indent):
        if isinstance(d, dict):
            space = ' '*indent
            return '{\n'+space + ',\n'.join('"{}": {}'.format(k, tree_to_json(v, indent)) for k, v in d.items()) + '\n}'
        elif isinstance(d, list):
            return '[' + ', '.join(tree_to_json(v, indent) for v in d) + ']'
        else:
            return json.dumps(d, indent=indent)
    return tree_to_json(tree_dict, indent)


def tree_dict_list2str(tree):
    for key, value in tree.items():
        if isinstance(value, list):
            tree[key] = str(value)
        elif isinstance(value, dict):
            tree_dict_list2str(value)
    return tree


def remove_spurious_patterns(text_dict):
    text_dict = replace_pattern(text_dict, '"[', '[')
    text_dict = replace_pattern(text_dict, ']"', ']')
    return text_dict

def replace_pattern(text, pattern1, pattern2):
    return text.replace(pattern1, pattern2)


def flatten_tree(tree):
    for key in tree:
        if isinstance(tree[key], dict):
            flatten_tree(tree[key])
        elif isinstance(tree[key], list) and len(tree[key]) == 1:
            tree[key] = tree[key][0]


def dict2hash(dict1):
    hex_dig = hashlib.sha256(json.dumps(dict1, sort_keys=True).encode()).hexdigest()
    return hex_dig


def DL2LD(tree: dict):
    for key, value in tree.items():
        if type(value) == dict:
            tree[key] = DL2LD(tree[key])
    keys = tree.keys()
    values = tree.values()
    combinations = list(product(*values))
    return [dict(zip(keys, combination)) for combination in combinations]


def LD2DL(dicts):
    merged = {}
    for d in dicts:
        for key, value in d.items():
            if key in merged and isinstance(value, dict):
                merged[key] = LD2DL([merged[key], value])
            elif key in merged and isinstance(value, (list, tuple, set)):
                if isinstance(merged[key], (list, tuple, set)):
                    merged[key] = list(set(merged[key] + value))
                else:
                    merged[key] = [merged[key]] + value
            elif key in merged and not isinstance(value, (list, tuple, set)):
                if isinstance(merged[key], (list, tuple, set)):
                    merged[key].append(value)
                else:
                    merged[key] = [merged[key], value]
            else:
                merged[key] = value
    return merged


def listify_leaves(tree: dict) -> dict:
    for key, value in tree.items():
        if isinstance(value, dict):
            # Recursively listify the leaves of the subtree
            tree[key] = listify_leaves(value)
        elif not isinstance(value, list):
            # Convert the leave into a list
            tree[key] = [value]
    return tree


def compare_structure(dict1, dict2):
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        keys1, keys2 = sorted(dict1.keys()), sorted(dict2.keys())
        if keys1 != keys2:
            return False
        for key in keys1:
            if not compare_structure(dict1[key], dict2[key]):
                return False
        return True
    elif not isinstance(dict1, dict) and not isinstance(dict2, dict):
        return True
    else:
        return False


def check_same_structure(tree_dicts:List[dict]):
    # Compare each dictionary with the first one
    for i in range(1, len(tree_dicts)):
        if not compare_structure(tree_dicts[0], tree_dicts[i]):
            return False, i
    return True, 0


def prune_tree_single_leaves(tree):
    keys_to_remove = []
    for key, value in tree.items():
        if isinstance(value, dict):
            prune_tree_single_leaves(value)
            if not value:
                keys_to_remove.append(key)
        elif not (isinstance(value, list) and len(value) > 1):
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del tree[key]


def extract_paths_from_dict(tree_dict, current_path=None):
    if current_path is None:
        current_path = []
    paths = []
    for key, value in tree_dict.items():
        new_path = current_path + [key]
        if isinstance(value, dict):
            paths.extend(extract_paths_from_dict(value, new_path))
        else:
            paths.append(new_path)
    return paths


def generate_dict_paths(tree, current_path=None):
    if current_path is None:
        current_path = []
    paths = []
    for key, value in tree.items():
        new_path = current_path + [key]
        if isinstance(value, dict):
            paths.extend(generate_dict_paths(value, new_path))
        else:
            paths.append(new_path)
    return paths


def walk_tree(tree_dict, parent_key=None):
    if not isinstance(tree_dict, dict):
        return
    directories = []
    files = []
    for key, value in tree_dict.items():
        if isinstance(value, dict):
            directories.append(key)
        else:
            files.append((key, value))
    yield parent_key, directories, files
    for directory in directories:
        yield from walk_tree(tree_dict[directory], directory)


def pretty_print_dict(d, indent=0):
    for key, value in d.items():
        if isinstance(value, dict):
            print('  ' * indent + str(key) + ':')
            pretty_print_dict(value, indent+1)
        else:
            print('  ' * indent + "• " + str(key) + ": " +str(value))


# def merge_subdicts(dicts_list:List[dict], key:str):
#     assert isinstance(dicts_list, list) and all( isinstance(d, dict) or isinstance(d.__dict__, dict) for d in dicts_list)
#     assert isinstance(key, str)
#     accepted_dicts = [ current_dict for current_dict in dicts_list if (key in current_dict)]
#     merged_dict = {}
#     for current_dict in accepted_dicts:
#         assert isinstance(current_dict[key], dict), "The entry '"+key+"' should be a dictionary."
#         merged_dict.update(copy.deepcopy(current_dict[key]))
#     return merged_dict
def merge_subdicts(dicts_list:list, key:Union[str,list], config_dict:bool=True):
    # assert isinstance(dicts_list, list) and all( isinstance(d, dict) or isinstance(d.__dict__, dict) for d in dicts_list)
    assert isinstance(key, (str,list))
    merged_dict = {}
    for current_dict in dicts_list:
        value = get_value_at_path(key, current_dict) if config_dict else get_value_at_path(key, current_dict)
        if value is not None:
            assert isinstance(value, dict), "The entry '"+key+"' should be a dictionary."
            merged_dict.update(copy.deepcopy(value))
    return merged_dict