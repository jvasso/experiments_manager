def generate_paths(tree, current_path=None):
    if current_path is None:
        current_path = []
    paths = []
    for key, value in tree.items():
        new_path = current_path + [key]
        if isinstance(value, dict):
            paths.extend(generate_paths(value, new_path))
        else:
            paths.append(new_path)
    return paths

# Example usage
tree_dict = {
    'a': {
        'b': {
            'c': 1,
            'd': 2
        },
        'e': 3
    },
    'f': {
        'g': 4
    }
}

paths = generate_paths(tree_dict)
for path in paths:
    print(" -> ".join(map(str, path)))
