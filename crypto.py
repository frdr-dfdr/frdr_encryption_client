#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
    crypto.py -e -n <dataset_name> -i <input_path> [-o <output_path>] [--hvac <vault_addr>] [--username <vault_username>] [--password <vault_password>] [--loglevel=<loglevel>] 
    crypto.py -d -i <input_path> [-o <output_path>] (--key <key_path> | --hvac <vault_addr> --username <vault_username> --password <vault_password> --url <API_path>) [--loglevel=<loglevel>] 
    crypto.py --logout_vault

Options:
    -e --encrypt           encrypt
    -d --decrypt           decrypt
    -n <dataset_name>, --name <dataset_name>
    -i <input_path>, --input <input_path>
    -o <output_path>, --output <output_path> 
    -k <key_path>, --key <key_path>
    --hvac <vault_addr> using hashicorp vault for key generation and storage
    -u <vault_username>, --username <vault_username>
    -p <vault_password>, --password <vault_password>
    --logout_vault  Remove old vault tokens
    --url <API_path>  API Path to fetch secret on vault
    -l --loglevel The logging level(debug, error, warning or info) [default: info]
"""
from docopt import docopt
import sys
import nacl.utils
import nacl.secret
import os
from util.util import Util
import hvac
from modules.VaultClient import VaultClient
from modules.KeyGenerator import KeyManagementLocal, KeyManagementVault
from appdirs import AppDirs
import logging

version = '0.0.1'
__version__ = version
EXCLUDED_FILES = [".*", 
                  "Thumbs.db", 
                  ".DS_Store", 
                  "._.DS_Store", 
                  ".localized", 
                  "desktop.ini", 
                  "*.pyc", 
                  "*.swx",
                  "*.swp", 
                  "*~", 
                  "~$*", 
                  "NULLEXT"]
app_name = "frdr-crypto"
app_author = "Compute Canada"
dirs = AppDirs(app_name, app_author)
os.makedirs(dirs.user_data_dir, exist_ok=True)
tokenfile = os.path.join(dirs.user_data_dir, "vault_token")

class Cryptor(object):
    def __init__(self, arguments, key_manager, logger):
        self._arguments = arguments
        self._key_manager = key_manager
        self._input = Util.clean_dir_path(self._arguments["--input"])
        self._output = self._arguments["--output"]
        self._logger = logger
        if self._arguments["--encrypt"]:
            dataset_name = self._arguments["--name"]
            if self._arguments["--hvac"]:
                self._secret_path = os.path.join(self._key_manager.get_vault_entity_id(), dataset_name)
            else:
                self._secret_path = "{}_key.pem".format(dataset_name)
            self._key_manager.generate_key()
        elif self._arguments["--decrypt"]:
            if self._arguments["--hvac"]:
                self._secret_path = "/".join(arguments["--url"].split("/")[-2:])
            else: 
                self._secret_path = self._arguments["--key"]
            self._key_manager.read_key(self._secret_path)
        else:
            # raise error
            pass
        self.box = nacl.secret.SecretBox(self._key_manager.key)

    def encrypt(self):
        logger = logging.getLogger('frdr-crypto.encrypt')
        # encrypt each file in the dirname
        if self._output is None:
            self._output = self._input + '_encrypted'
        if os.path.isdir(self._input):
            all_files, all_subdirs = self._get_files_list(self._input)
            self._create_output_dirs(all_subdirs)
            for each_file in all_files:
                try:
                    self._encrypt_file(each_file, logger)
                except AssertionError:
                    logger.warning("File {} was not encrypted successfully.".format(each_file))
        else:
            self._encrypt_file(self._input, logger)
        # save key
        self._key_manager.save_key(self._secret_path)

        # create dataset access policy and group if they don't exist
        if self._arguments["--hvac"]:
            self._key_manager.create_access_policy_and_group()

    def decrypt(self):
        logger = logging.getLogger('frdr-crypto.decrypt')
        if self._output is None:
            self._output = self._input + '_decrypted'
        if os.path.isdir(self._input):
            all_files, all_subdirs = self._get_files_list(self._input)
            self._create_output_dirs(all_subdirs)
            for each_file in all_files:
                self._decrypt_file(each_file, logger)
        else:
            self._decrypt_file(self._input, logger)   
        
    def _encrypt_file(self, filename, logger):
        if self._file_excluded(filename, EXCLUDED_FILES):
            return False
        encrypted_filename = os.path.join(os.path.dirname(filename), os.path.basename(filename) + ".encrypted")
        if os.path.isdir(self._input):
            with open(os.path.join(self._input, filename), 'rb') as f:
                message = f.read()
            encrypted = self.box.encrypt(message)
            with open(os.path.join(self._output, encrypted_filename), 'wb') as f:
                f.write(encrypted)
            assert len(encrypted) == len(message) + self.box.NONCE_SIZE + self.box.MACBYTES
        else:
            with open(filename, 'rb') as f:
                message = f.read()
            encrypted = self.box.encrypt(message)
            with open(encrypted_filename, 'wb') as f:
                f.write(encrypted) 
        logger.info("File {} is encrypted.".format(filename))
        return True

    def _decrypt_file(self, filename, logger):
        decrypted_filename = os.path.join(os.path.dirname(filename), '.'.join(os.path.basename(filename).split('.')[:-1]))
        if os.path.isdir(self._input):
            with open(os.path.join(self._input, filename), 'rb') as f:
                encrypted_message = f.read()
            decrypted = self.box.decrypt(encrypted_message)
            with open(os.path.join(self._output, decrypted_filename), 'wb') as f:
                f.write(decrypted)
        else:
            with open(filename, 'rb') as f:
                encrypted_message = f.read()
            decrypted = self.box.decrypt(encrypted_message)
            with open(decrypted_filename, 'wb') as f:
                f.write(decrypted)
        logger.info("File {} is decrypted.".format(filename))
        return True

    # get relative path of all files in the input dir
    # return relative paths of all files and subdirs in the dir
    def _get_files_list(self, dirname):  
        files_list = os.listdir(dirname)
        all_files = list()
        all_subdirs = list()
        for entry in files_list:
            full_path = os.path.join(dirname, entry)
            relative_path = os.path.relpath(full_path, self._input)
            if os.path.isdir(full_path):
                all_subdirs.append(relative_path)
                current_files, current_dirs = self._get_files_list(full_path)
                all_subdirs = all_subdirs + current_dirs
                all_files = all_files + current_files
            else:
                all_files.append(relative_path)
        return all_files, all_subdirs
    
    def _create_output_dirs(self, dirs):
        Util.make_dir(self._output)
        for each_dir_rel_path in dirs:
            Util.make_dir(os.path.join(self._output, each_dir_rel_path))

    def _file_excluded(self, filepath, excluded_list):
        """Return True if path or ext in excluded_files list """
        filename = os.path.basename(filepath)
        extension = os.path.splitext(filename)[1][1:].strip().lower()
        # check for filename in excluded_files set
        if filename in excluded_list:
            return True
        # check for extension in and . (dot) files in excluded_files
        if (not extension and 'NULLEXT' in excluded_list) or '*.' + extension in excluded_list or \
                (filename.startswith('.') and u'.*' in excluded_list) or \
                (filename.endswith('~') and u'*~' in excluded_list) or \
                (filename.startswith('~$') and u'~$*' in excluded_list):
            return True
        return False 

if __name__ == "__main__":
    try:
        if sys.version_info[0] < 3:
            raise Exception("Python 3 is required to run the local client.")
        arguments = docopt(__doc__, version=__version__)
        logger = Util.get_logger("frdr-crypto", 
                                log_level=arguments["--loglevel"],
                                filepath=os.path.join(dirs.user_data_dir, "frdr-crypto_log.txt"))
        if arguments['--logout_vault']:
            try:
                os.remove(tokenfile)
            except:
                pass
            logger.info("Removed old auth tokens. Exiting.")
            sys.exit()
        if arguments["--hvac"]:
            vault_client = VaultClient(arguments["--hvac"], arguments["--username"], arguments["--password"], tokenfile)
            #TODO: use dataset uuid instead of name
            dataset_name = arguments["--name"]
            if dataset_name is None:
                dataset_name = arguments["--url"].split("/")[-1]
            key_manager = KeyManagementVault(vault_client, dataset_name)
        else:
            key_manager = KeyManagementLocal()
        encryptor = Cryptor(arguments, key_manager, logger)
        if arguments["--encrypt"]:
            encryptor.encrypt()
        elif arguments["--decrypt"]:
            encryptor.decrypt()
        else:
            pass
    except Exception as e:
        exit