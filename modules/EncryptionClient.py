#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import nacl.utils
import nacl.secret
import os
from util.util import Util
from config import app_config, person_key_server_config
import logging
import shutil
import tempfile
from zipfile import ZipFile
import bagit
import re

class EncryptionClient(object):
    def __init__(self, dataset_key_manager, person_key_manager, input_dir=None, output_dir=None):
        self._dataset_key_manager = dataset_key_manager
        self._person_key_manager = person_key_manager
        if input_dir is not None:
            self._input = Util.clean_dir_path(input_dir)
        self._output = output_dir

    def encrypt(self, dataset_uuid):
        logger = logging.getLogger('fdrd-encryption-client.encrypt')

        # generate key 
        self._dataset_key_manager.generate_key()
        self.box = nacl.secret.SecretBox(self._dataset_key_manager.key)

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
            self._encrypt_file(zip_filepath, logger)
            os.remove(zip_filepath)
        else:
            self._encrypt_file(self._input, logger)
        
        try:
            bag = bagit.make_bag(bag_dir, None, 1, ['sha256'])
            bag.info['Depositor-Entity-ID'] = self._dataset_key_manager.get_vault_entity_id()
            bag.info['Dataset-UUID'] = dataset_uuid
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
        self._dataset_key_manager.encrypt_key(self._person_key_manager.my_public_key)
        self._dataset_key_manager.save_key("/".join([dataset_key_server_config.VAULT_DATASET_KEY_PATH, self._dataset_key_manager.get_vault_entity_id(), dataset_uuid]))
        
        return bag_output_path

    def decrypt(self, url):
        logger = logging.getLogger('fdrd-encryption-client.decrypt')

        depositor_uuid, dataset_uuid, requester_uuid = self._parse_url(url)
        if requester_uuid == "" :
            assert self._dataset_key_manager.get_vault_entity_id() == depositor_uuid, "The url you provide is not correct"
            encrypted_data_key_path =  "/".join([dataset_key_server_config.VAULT_DATASET_KEY_PATH, depositor_uuid, dataset_uuid])
        else:
            encrypted_data_key_path = "/".join([dataset_key_server_config.VAULT_DATASET_KEY_PATH, depositor_uuid, dataset_uuid, requester_uuid])
        self._dataset_key_manager.read_key(encrypted_data_key_path)
        private_key_path = os.path.join(Util.get_key_dir(self._dataset_key_manager.get_vault_entity_id()), person_key_server_config.LOCAL_PRIVATE_KEY_FILENAME)
        user_private_key = self._person_key_manager.read_private_key(private_key_path)
        self._dataset_key_manager.decrypt_key(user_private_key)
        self.box = nacl.secret.SecretBox(self._dataset_key_manager.key)

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

    def grant_access(self, requester_entity_id, dataset_id, expiry_date=None):
        if expiry_date is None:
            expiry_date = (datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")

        # read encrypted data key from Vault
        encrypted_data_key_path = "/".join([dataset_key_server_config.VAULT_DATASET_KEY_PATH, self._dataset_key_manager.get_vault_entity_id(), dataset_id])
        self._dataset_key_manager.read_key(encrypted_data_key_path)
        
        # decrypt the encrypted data key with the depositor private key
        private_key_path = os.path.join(Util.get_key_dir(self._dataset_key_manager.get_vault_entity_id()), person_key_server_config.LOCAL_PRIVATE_KEY_FILENAME)
        depositor_private_key = self._person_key_manager.read_private_key(private_key_path)
        self._dataset_key_manager.decrypt_key(depositor_private_key)

        # encrypt the encrypted data key with the requester public key
        requester_public_key = self._person_key_manager.read_public_key_from_vault(requester_entity_id)
        self._dataset_key_manager.encrypt_key(requester_public_key)
        path_on_vault = "/".join([dataset_key_server_config.VAULT_DATASET_KEY_PATH, self._dataset_key_manager.get_vault_entity_id(), dataset_id, requester_entity_id])
        self._dataset_key_manager.set_key_expiry_date(path_on_vault, expiry_date)
        self._dataset_key_manager.save_key(path_on_vault)
        
    def _encrypt_file(self, filename, logger):
        if self._file_excluded(filename, app_config.EXCLUDED_FILES):
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
                if self._file_excluded(filename, app_config.EXCLUDED_FILES):
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

    def _parse_url(self, url):
        print (url)
        match = re.match(r"^.*secret/data/dataset/([0-9a-f\-]*)/([0-9a-f\-]*)/?(.*)?", url)
        depositor_uuid = match.group(1)
        dataset_uuid = match.group(2)
        requester_uuid = match.group(3)
        return (depositor_uuid, dataset_uuid, requester_uuid)
