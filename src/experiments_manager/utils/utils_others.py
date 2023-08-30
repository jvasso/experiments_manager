import pickle
import os


def save_object_under_name(name, my_object):
    with open(name, 'wb') as file:
        pickle.dump(my_object, file, pickle.HIGHEST_PROTOCOL)


def load_pickle_object(name):
    if os.path.isfile(name):
        with open(name, 'rb') as file:
            my_object = pickle.load(file)
        return my_object
    return None