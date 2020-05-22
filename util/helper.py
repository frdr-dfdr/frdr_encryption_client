import os
from base64 import b64encode, b64decode
def make_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        #TODO: log
    else:
        #TODO: log already existed 
        pass

def base64_to_byte(plaintext):
    return b64decode(plaintext.encode())

def clean_dir_path(path):
    if path.endswith(os.sep):
        return path[:-1]
    else:
        return path