import json
import hashlib
from itertools import product

import pprint

import time

import pdb
print('o,')

def dict2hash(dict1):
    # hex_dig = hashlib.sha256(json.dumps(dict1, sort_keys=True).encode()).hexdigest()
    hex_dig = hashlib.sha1(json.dumps(dict1, sort_keys=True).encode()).hexdigest()
    return hex_dig

def DL2LD(tree: dict):
    for key, value in tree.items():
        if type(value) == dict:
            tree[key] = DL2LD(tree[key])
    keys = tree.keys()
    values = tree.values()
    combinations = list(product(*values))
    return [dict(zip(keys, combination)) for combination in combinations]

def generate_dicts(nb_keys, nb_val_per_key):
    dict_of_lists = { "key"+str(idx_key):list(range(nb_val_per_key)) for idx_key in range(nb_keys) }
    list_of_dicts = DL2LD(dict_of_lists)
    print("List of size "+str(len(list_of_dicts)))
    return list_of_dicts

def compare_hashes(target_hash, list_of_hashes):
    for idx in range(len(list_of_hashes)):
        hash = list_of_hashes[idx]
        if hash == target_hash:
            print("found at idx "+str(idx))
            return idx
    print("not found")

# nb_hyperparams_keys = 10
# nb_val_per_key = 5
nb_hyperparams_keys = 10
nb_val_per_key = 5

start1 = time.time()
list_of_dicts = generate_dicts(nb_hyperparams_keys, nb_val_per_key)
my_dict = list_of_dicts[-1]
end1 = time.time()
total1 = end1 - start1
print("\nGenerating dicts took "+str(total1)+ " seconds.")

start2 = time.time()
my_hashed_dict = dict2hash(my_dict)
list_of_hashed_dicts = [ dict2hash(current_dict)  for current_dict in list_of_dicts ]
end2 = time.time()
total2 = end2 - start2
print("\nBuilding hashes took "+str(total2)+ " seconds.")

start3 = time.time()
compare_hashes(my_hashed_dict, list_of_hashed_dicts)
end3 = time.time()
total3 = end3-start3
print("\nComparing hashes took "+str(total3)+ " seconds.")
print(str(len(list_of_dicts)/total3) + " comparisons per second.")


pdb.set_trace()