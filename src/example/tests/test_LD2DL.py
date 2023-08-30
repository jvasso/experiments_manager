# import pdb
# import pprint

# def LD2DL(dicts):
#     merged = {}
#     for d in dicts:
#         for key, value in d.items():
#             if key in merged and isinstance(value, dict):
#                 merged[key] = LD2DL([merged[key], value])
#             elif key in merged and isinstance(value, (list, tuple, set)):
#                 if isinstance(merged[key], (list, tuple, set)):
#                     merged[key] = list(set(merged[key] + value))
#                 else:
#                     merged[key] = [merged[key]] + value
#             elif key in merged and not isinstance(value, (list, tuple, set)):
#                 if isinstance(merged[key], (list, tuple, set)):
#                     merged[key].append(value)
#                 else:
#                     merged[key] = [merged[key], value]
#             else:
#                 merged[key] = value
#     return merged



# my_dict1 = {
#     "a":0,
#     "b":[1],
#     "c":{
#         "d":2,
#         "e":3
#     }
# }
# my_dict2 = {
#     "a":4,
#     "b":5,
#     "c":{
#         "d":[6],
#         "e":7,
#         "f":10
#     }
# }

# mylist = [my_dict1, my_dict2]

# nveau_dict = LD2DL(mylist)

# pprint.pprint(nveau_dict)

# pdb.set_trace()


def compare_structure(dict1, dict2):
    # Check if both are dictionaries
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        # Get the keys from both dictionaries and sort them
        keys1, keys2 = sorted(dict1.keys()), sorted(dict2.keys())
        
        # Compare keys at the current level
        if keys1 != keys2:
            return False
        
        # Recursively compare nested dictionaries
        for key in keys1:
            if not compare_structure(dict1[key], dict2[key]):
                return False
                
        return True

    # Check if both are non-dictionary items
    elif not isinstance(dict1, dict) and not isinstance(dict2, dict):
        return True

    else:
        return False

def check_same_structure(tree_dicts):
    # Compare each dictionary with the first one
    for i in range(1, len(tree_dicts)):
        if not compare_structure(tree_dicts[0], tree_dicts[i]):
            return False
    return True

# Example usage:
tree_dict1 = {'a': {'b': {'c': [1]}}, 'd': 2}
tree_dict2 = {'a': {'b': {'c': 3}}, 'd': [4]}
tree_dict3 = {'a': {'b': {'c': 5}}, 'd': 6}
tree_dict4 = {'a': {'b': {'c': 7, 'extra_key': 8}}, 'd': 9}  # Different structure

tree_dicts = [tree_dict1, tree_dict2, tree_dict3]
print(check_same_structure(tree_dicts))  # Should now return True

tree_dicts = [tree_dict1, tree_dict2, tree_dict4]
print(check_same_structure(tree_dicts))  # Should return False

