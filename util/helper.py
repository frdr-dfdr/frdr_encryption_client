import os
def make_dir(dir_name):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        #TODO: log
    else:
        #TODO: log already existed 
        pass