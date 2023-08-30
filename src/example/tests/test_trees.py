def extract_paths_only(tree_dict, current_path=None):
    if current_path is None:
        current_path = []
        
    paths = []
    
    for key, value in tree_dict.items():
        new_path = current_path + [key]
        
        if isinstance(value, dict):
            paths.extend(extract_paths_only(value, new_path))
        else:
            paths.append(new_path)
    
    return paths

# Example usage:
tree = {
    'a': {
        'b': [1],
        'c': {
            'd': [2],
            'e': 3
        }
    },
    'f': {
        'g': 4
    }
}

paths = extract_paths_only(tree)
print(paths)
