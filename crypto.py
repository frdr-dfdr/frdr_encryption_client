#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
    crypto.py -e -i <input_path> [-o <output_path>] [--vault <vault_addr>] [--username <vault_username>] [--password <vault_password>] [--loglevel=<loglevel>] 
    crypto.py -d -i <input_path> [-o <output_path>] (--key <key_path> | --vault <vault_addr> --username <vault_username> --password <vault_password> --url <API_path>) [--loglevel=<loglevel>] 
    crypto.py --logout_vault

Options:
    -e --encrypt           encrypt
    -d --decrypt           decrypt
    -i <input_path>, --input <input_path>
    -o <output_path>, --output <output_path> 
    -k <key_path>, --key <key_path>
    --vault <vault_addr> using hashicorp vault for key generation and storage
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
from util import constants
import hvac
from modules.VaultClient import VaultClient
from modules.KeyGenerator import KeyManagementLocal, KeyManagementVault
from appdirs import AppDirs
import logging
import uuid
import shutil
import tempfile
from zipfile import ZipFile
import bagit
import click

__version__ = constants.VERSION
dirs = AppDirs(constants.APP_NAME, constants.APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)
tokenfile = os.path.join(dirs.user_data_dir, "vault_token")

class Cryptor(object):
    def __init__(self, arguments, key_manager, logger, dataset_name):
        self._arguments = arguments
        self._key_manager = key_manager
        self._input = Util.clean_dir_path(self._arguments["--input"])
        self._output = self._arguments["--output"]
        self._logger = logger
        self._dataset_name = dataset_name
        if self._arguments["--encrypt"]:
            if self._arguments["--vault"]:
                self._secret_path = os.path.join(self._key_manager.get_vault_entity_id(), dataset_name)
            else:
                self._secret_path = "{}_key.pem".format(dataset_name)
            self._key_manager.generate_key()
        elif self._arguments["--decrypt"]:
            if self._arguments["--vault"]:
                self._secret_path = "/".join(arguments["--url"].split("/")[-2:])
            else: 
                self._secret_path = self._arguments["--key"]
            self._key_manager.read_key(self._secret_path)
        else:
            self._logger.error("Argument (encrypt or decrypt) is not provided.")
            raise Exception
        self.box = nacl.secret.SecretBox(self._key_manager.key)

    def encrypt(self):
        logger = logging.getLogger('frdr-crypto.encrypt')
        bag_dir_parent = tempfile.mkdtemp()
        if os.path.isdir(bag_dir_parent):
            shutil.rmtree(bag_dir_parent)
        bag_dir = os.path.join(bag_dir_parent, 'bag')
        #TODO: check the difference between makedirs and mkdir
        os.makedirs(bag_dir)   
        # encrypt each file in the dirname
        # TODO: move this to the init function
        if self._output is None:
            # default output path is the desktop
            self._output = os.path.expanduser("~/Desktop/")
        
        if os.path.isdir(self._input):
            zip_filepath = self._compress_folder(self._input, bag_dir)
            self._logger.info(zip_filepath) 
            self._encrypt_file(zip_filepath, logger)
            os.remove(zip_filepath)
        else:
            self._encrypt_file(self._input, logger)
        
        try:
            bag = bagit.make_bag(bag_dir, None, 1, ['sha256'])
            bag.info['Depositor-Entity-ID'] = self._key_manager.get_vault_entity_id()
            bag.info['Datast-UUID'] = self._dataset_name
            bag.save()
        except (bagit.BagError, Exception) as e:
            # TODO: log error
            return False
        
        # zip bag dir and move it to the output path
        bag_destination = os.path.join(str(bag_dir_parent), (os.path.basename(self._input)+"_bag"))
        zipname = shutil.make_archive(bag_destination, 'zip', bag_dir)
        shutil.rmtree(bag_dir)
        bag_output_path = os.path.join(self._output, os.path.basename(zipname))
        shutil.move(zipname, bag_output_path)

        # save key
        self._key_manager.save_key(self._secret_path)

        # create dataset access policy and group if they don't exist
        if self._arguments["--vault"]:
            self._key_manager.create_access_policy_and_group()
        
        return bag_output_path

    def decrypt(self):
        logger = logging.getLogger('frdr-crypto.decrypt')
        if self._output is None:
            # default output path is the desktop
            self._output = os.path.expanduser("~/Desktop/")
        # if the input is the decrypted package
        if os.path.basename(self._input).endswith("encrypted"):
            decrypted_filename = self._decrypt_file(self._input, logger)  
            shutil.move(decrypted_filename, os.path.join(self._output, os.path.basename(decrypted_filename))) 
        # if the input is the zipped bag
        else:
            bag_dir_parent = tempfile.mkdtemp()
            if os.path.isdir(bag_dir_parent):
                shutil.rmtree(bag_dir_parent)
            bag_dir = os.path.join(bag_dir_parent, 'bag')
            shutil.unpack_archive(self._input, bag_dir, "zip")
            for root, dirs, files in os.walk(os.path.join(bag_dir, "data")):
                for filename in files:
                    encrypted_filename = os.path.join(root, filename)
            decrypted_filename = self._decrypt_file(encrypted_filename, logger)
            shutil.move(decrypted_filename, os.path.join(self._output, os.path.basename(decrypted_filename)))
            shutil.rmtree(bag_dir_parent)
        return True
        
    def _encrypt_file(self, filename, logger):
        if self._file_excluded(filename, constants.EXCLUDED_FILES):
            return False
        encrypted_filename = os.path.join(os.path.dirname(filename), os.path.basename(filename) + ".encrypted")
        with open(filename, 'rb') as f:
            message = f.read()
        encrypted = self.box.encrypt(message)
        with open(encrypted_filename, 'wb') as f:
            f.write(encrypted) 
        assert len(encrypted) == len(message) + self.box.NONCE_SIZE + self.box.MACBYTES
        logger.info("File {} is encrypted.".format(filename))
        return True

    def _decrypt_file(self, filename, logger):
        decrypted_filename = os.path.join(os.path.dirname(filename), '.'.join(os.path.basename(filename).split('.')[:-1])) 
        with open(filename, 'rb') as f:
            encrypted_message = f.read()
        decrypted = self.box.decrypt(encrypted_message)
        with open(decrypted_filename, 'wb') as f:
            f.write(decrypted)
        logger.info("File {} is decrypted.".format(filename))
        return decrypted_filename

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

    def _compress_folder(self, input_path, output_path, filter=False):
        if filter:
            # for each file in the folder
            all_files, all_subdirs = self._get_files_list(input_path)
            zipfile_name = os.path.join(output_path, os.path.basename(input_path) + ".zip")
            zip_obj = ZipFile(zipfile_name, "w")
            for filename in all_files:
                if self._file_excluded(filename, constants.EXCLUDED_FILES):
                    pass
                else:
                    zip_obj.write(os.path.join(input_path, filename))
            # Required as there can be subdirs with no files in them
            for subdir in all_subdirs:
                zip_obj.write(os.path.join(input_path, subdir))
            zip_obj.close()
        else:
            zipfile_path = os.path.join(output_path, os.path.basename(input_path))
            zipfile_name = shutil.make_archive(zipfile_path, 'zip', input_path)
        return zipfile_name

if __name__ == "__main__":
    try:
        arguments = docopt(__doc__, version=__version__)
        logger = Util.get_logger("frdr-crypto", 
                                log_level=arguments["--loglevel"],
                                filepath=os.path.join(dirs.user_data_dir, "frdr-crypto_log.txt"))
        if sys.version_info[0] < 3:
            raise Exception("Python 3 is required to run the local client.")
        if arguments['--logout_vault']:
            try:
                os.remove(tokenfile)
            except:
                pass
            logger.info("Removed old auth tokens. Exiting.")
            sys.exit()
        if arguments["--vault"]:
            vault_client = VaultClient(arguments["--vault"], arguments["--username"], arguments["--password"], tokenfile)
            if arguments["--encrypt"]:
                dataset_name = str(uuid.uuid4()) 
            elif arguments["--decrypt"]:
                dataset_name = arguments["--url"].split("/")[-1]
            else:
                raise Exception
            key_manager = KeyManagementVault(vault_client, dataset_name)
        else:
            key_manager = KeyManagementLocal()
            dataset_name = str(uuid.uuid4()) 
        encryptor = Cryptor(arguments, key_manager, logger, dataset_name)
        if arguments["--encrypt"]:
            encryptor.encrypt()
        elif arguments["--decrypt"]:
            warning_string = "You are trying to decrypt the dataset {dataset_id}"\
                             .format(dataset_id=dataset_name)
            print (Util.wrap_text(warning_string))
            if click.confirm("Do you want to continue?", default=False):  
                encryptor.decrypt()
        else:
            pass
    except Exception as e:
        logger.error("Exception caught, exiting. {}".format(e))
        exit