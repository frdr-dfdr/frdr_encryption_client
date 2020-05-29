import os
import sys
import logging
from base64 import b64encode, b64decode
class Util(object):
    
    @classmethod
    def make_dir(cls, dir_name):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
            #TODO: log
        else:
            #TODO: log already existed 
            pass
   
    @classmethod
    def base64_to_byte(cls, plaintext):
        return b64decode(plaintext.encode())

    @classmethod
    def clean_dir_path(cls, path):
        if path.endswith(os.sep):
            return path[:-1]
        else:
            return path

    @classmethod
    def get_logger(cls, name, log_level="INFO", filepath=None):
        logger = logging.getLogger(name)
        # if logger already exists, return it
        if logger.handlers:
            return logger
        
        level = getattr(logging, log_level.upper() if log_level else "INFO")
        try:
            logger.setLevel(level)
        except: 
            logger.setLevel(logging.INFO)

        logger.info("Log level: {}".format(log_level))

        clean_logformatter = '%(message)s'
        clean_formatter = logging.Formatter(clean_logformatter)
        console = logging.StreamHandler(sys.stdout)
        try:
            console.setLevel(level)
        except: 
            console.setLevel(logging.INFO)

        # console.addFilter(lambda record: record.levelno <= logging.INFO)
        console.setFormatter(clean_formatter)
        logger.addHandler(console)
        
        # Create handlers
        if filepath:
            logformatter = '%(asctime)s [%(levelname)s] %(message)s'
            formatter = logging.Formatter(logformatter, '%Y-%m-%d %H:%M:%S')
            file_handler = logging.FileHandler(filepath, encoding='utf-8')
            try:
                file_handler.setLevel(level)
            except:
                file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)


        return logger