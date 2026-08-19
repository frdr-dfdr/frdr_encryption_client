#
# Copyright (c) 2024 Digital Research Alliance of Canada
#
# This file is part of FRDR Encryption Application.
#
# FRDR Encryption Application is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the FRDR Encryption Application Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# FRDR Encryption Application is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRDR Encryption Application. If not, see <https://www.gnu.org/licenses/>.
#

from ctypes import c_char_p
import datetime
import json
from multiprocessing import Process, Manager, Queue
import multiprocessing
import shutil
import webbrowser
from modules.PersonKeyManager import PersonKeyManager
from modules.EncryptionClient import EncryptionClient
from appdirs import AppDirs
import sys
import os
from modules.VaultClient import VaultClient
from util.configLoader import config
import logging
from util.util import Util
import uuid
from modules.DatasetKeyManager import DatasetKeyManager
from modules.FRDRAPIClient import FRDRAPIClient
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

import zmq

__version__ = config.VERSION
dirs = AppDirs(config.APP_NAME, appauthor=False, roaming=True)
os.makedirs(dirs.user_data_dir, exist_ok=True)

def encrypt_in_new_process(input_path, output_path, vault_client_token, 
                       vault_client_entity_id, vault_client_addr, 
                       return_message, queue):
    try:
        Util.get_logger("frdr-encryption-application",
                        log_level="info",
                        filepath=os.path.join(dirs.user_data_dir, config.APP_LOG_FILENAME))
        logger = logging.getLogger("frdr-encryption-application.gui.encrypt")
        logger.info("Encrypt files in the path {}".format(input_path))
        with open(os.path.join(dirs.user_data_dir, "pid"), 'w') as f:
            f.write(str(os.getpid()))
        dataset_uuid = str(uuid.uuid4())
        vault_client = VaultClient(token=vault_client_token, entity_id=vault_client_entity_id, url=vault_client_addr)
        dataset_key_manager = DatasetKeyManager(vault_client)
        person_key_manager = PersonKeyManager(vault_client)
        encryptor = EncryptionClient(
            dataset_key_manager, person_key_manager, input_path, output_path)
        bag_path = encryptor.encrypt(dataset_uuid, queue)
        return_message.value = bag_path
    except Exception as e:
        return_message.value = str(e)
        logger.error(e, exc_info=True)
        sys.exit(-1)

class EncryptionClientGui(object):
    def __init__(self):
        Util.get_logger("frdr-encryption-application",
                        log_level="info",
                        filepath=os.path.join(dirs.user_data_dir, config.APP_LOG_FILENAME))
        self._logger = logging.getLogger("frdr-encryption-application.gui")
        self._vault_client = VaultClient()
        self._frdr_api_client = FRDRAPIClient(base_url = config.FRDR_API_BASE_URL)
        # self._vault_client_pki = VaultClient()

    def login_oidc_google(self, hostname):
        try:
            self._logger.info(
                "Log into Vault using oidc method with google acccount")
            self._vault_client.login(vault_addr=hostname,
                                     auth_method="oidc",
                                     oauth_type="google")
            return (True, None)
        except Exception as e:
            self._logger.error(str(e), exc_info=True)
            return (False, str(e))

    def login_oidc_globus(self, success_msg, hostname=config.VAULT_HOSTNAME, hostname_pki=None):
        try:
            self._logger.info(
                "Log into Vault using oidc method with globus acccount")
            self._vault_client.login(vault_addr=hostname,
                                     auth_method="oidc",
                                     success_msg=success_msg)
            # self._vault_client_pki.login(vault_addr=hostname_pki,
            #                          auth_method="oidc")
            return (True, None)
        except Exception as e:
            self._logger.error(str(e), exc_info=True)
            return (False, str(e))

    def login_frdr_api_globus(self, success_msg):
        try:
            self._logger.info(
                "Login with globus acccount for FRDR REST API usage")
            self._frdr_api_client.login(success_msg=success_msg)
            return (True, None)
        except Exception as e:
            self._logger.error(str(e), exc_info=True)
            return (False, str(e))

    def logout(self):
        try:
            self._vault_client.logout()
            webbrowser.open(config.GLOBUS_LOGOUT_URL)
            self._logger.info("Log out successfully")
            return (True, None)
        except Exception as e:
            self._logger.error(str(e))
            return (False, str(e))

    def encrypt(self, input_path, output_path):
        manager = Manager()
        message = manager.Value(c_char_p, "")
        queue = Queue()
        p = Process(target=encrypt_in_new_process, args=(input_path, output_path, self._vault_client.token, self._vault_client.entity_id, self._vault_client.url, message, queue))
        p.start()
        p.join()

        self._logger.debug("Encryption process exitcode {}".format(p.exitcode))
        
        if (p.exitcode == 0):
            successful = True
        else:
            successful = False
            # Get the directories created when encrypting data if any.
            try: 
                temp_bag_dir = queue.get(timeout=0)
            except:
                temp_bag_dir = None
            try: 
                sums_fullpath = queue.get(timeout=0)
            except:
                sums_fullpath = None
            try:
                bag_output_path = queue.get(timeout=0)
            except:
                bag_output_path = None

            self.cleanup_failed_encryption(sums_fullpath, temp_bag_dir, bag_output_path)
            if (p.exitcode == -9):
                message.value = "Failed. The machine is out of memory."
            elif (p.exitcode == -15 or p.exitcode == 1):
                message.value = "Terminated by user."
        queue.close()
        return (successful, message.value)
    
    def cleanup_failed_encryption(self, sums_fullpath=None, temp_bag_dir=None, bag_output_path=None):
        self._logger.info("Clean up after failed encryption.")
        # delete checksum file in input data directory
        if sums_fullpath is not None and os.path.exists(sums_fullpath):
            self._logger.info("Deleting generated checksum file {}".format(sums_fullpath))
            os.remove(sums_fullpath)
        # delete temp dir
        if temp_bag_dir is not None and os.path.exists(temp_bag_dir) and os.path.isdir(temp_bag_dir):
            self._logger.info("Deleting temp dir {}".format(temp_bag_dir))
            shutil.rmtree(temp_bag_dir)
        # delete output dir
        if bag_output_path is not None and os.path.exists(bag_output_path):
            self._logger.info("Deleting output package {}".format(bag_output_path))
            os.remove(bag_output_path)

    def decrypt(self, input_path, output_path, url):
        try:
            self._logger.info(
                "Decrypt files in the path {}".format(input_path))
            dataset_key_manager = DatasetKeyManager(self._vault_client)
            person_key_manager = PersonKeyManager(self._vault_client)
            encryptor = EncryptionClient(
                dataset_key_manager, person_key_manager, input_path, output_path)
            encryptor.decrypt(url)
            _, dataset_uuid, requester_uuid = Util.parse_url(url)
            data = {"vault_dataset_id": dataset_uuid, "vault_requester_id": requester_uuid}
            self._frdr_api_client.update_requestitem_decrypt(data)
            return (True, None)
        except Exception as e:
            self._logger.info(str(e))
            return (False, str(e))

    def grant_access(self, dataset_uuid, requester_uuid, expire_date=None):
        try:
            if expire_date is None:
                expire_date = (datetime.date.today() + datetime.timedelta(days=30*6)).strftime("%Y-%m-%d")
            
            self._frdr_api_client.verify_requestitem_grant_access(dataset_uuid, requester_uuid)
            dataset_key_manager = DatasetKeyManager(self._vault_client)
            person_key_manager = PersonKeyManager(self._vault_client)
            encryptor = EncryptionClient(
                dataset_key_manager, person_key_manager)
            encryptor.grant_access(requester_uuid, dataset_uuid, expire_date)
            data = {"expires": expire_date, "vault_dataset_id": dataset_uuid,
                    "vault_requester_id": requester_uuid}
            self._frdr_api_client.update_requestitem_grant_access(data)
            return (True, None)
        except Exception as e:
            self._logger.error(e, exc_info=True)
            return (False, str(e))
    
    def verify_local_keys(self):
        person_key_manager = PersonKeyManager(self._vault_client)
        error_msg = None
        try:
            person_key_manager.create_or_retrieve_public_key()
        except ValueError as e:
            self._logger.error(e, exc_info=True)
            error_msg = str(e)
        except FileNotFoundError as e:
            self._logger.error(e, exc_info=True)
            error_msg = "No public key is found locally."
        try:
            private_key_path = os.path.join(Util.get_key_dir(
                person_key_manager.get_vault_entity_id()), config.LOCAL_PRIVATE_KEY_FILENAME)
            person_key_manager.read_private_key(private_key_path)
        except FileNotFoundError as e:
            self._logger.error(e, exc_info=True)
            if error_msg is not None:
                error_msg = error_msg + "\nNo private key is found locally." 
            else:
                error_msg = "No private key is found locally."

        return error_msg

    def import_private_key_from_file(self, source_file_path):
        """
        Import and save a private key from a file.

        Args:
            source_file_path (str): Path to the source private key file.

        Returns:
            tuple: (success: bool, message: str)
        """
        person_key_manager = PersonKeyManager(self._vault_client)
        
        try:
            entity_id = person_key_manager.get_vault_entity_id()
            if not entity_id:
                return (False, "Unable to retrieve vault entity ID.")
            
            public_key = person_key_manager.get_public_key()
            if public_key is None:
                return (False, "No public key found on vault or locally.")
            
            if not os.path.exists(source_file_path):
                return (False, f"Source file not found: {source_file_path}")
            
            # Determine destination path
            key_dir = Util.get_key_dir(entity_id)
            os.makedirs(key_dir, exist_ok=True)
            
            dest_file_path = os.path.join(key_dir, config.LOCAL_PRIVATE_KEY_FILENAME)
            
            # Backup existing key if present
            if os.path.exists(dest_file_path):
                backup_path = dest_file_path + '.backup'
                shutil.copy2(dest_file_path, backup_path)
                self._logger.info(f"Backed up existing private key to {backup_path}")
            
            # Copy the file
            shutil.copy2(source_file_path, dest_file_path)
            
            # Set permissions
            os.chmod(dest_file_path, 0o600)
            
            # Verify the key
            private_key = person_key_manager.read_private_key(dest_file_path)
            if not Util.verify_key_pair_match(public_key, private_key):
                # Verification failed, remove the imported key
                os.remove(dest_file_path)
                return (False, "The imported private key does not match the public key on vault.")
            
            self._logger.info(f"Private key imported successfully from {source_file_path}")
            return (True, "Private key imported and verified successfully.")
            
        except Exception as e:
            self._logger.error(f"Error importing private key from file: {e}", exc_info=True)
            return (False, f"Error importing private key: {str(e)}")


    def import_private_key_from_text(self, key_content):
        """
        Import and save a private key from text content
        
        Args:
            key_content (str): The private key content as a string
            
        Returns:
            tuple: (success: bool, message: str)
        """
        person_key_manager = PersonKeyManager(self._vault_client)
        
        try:
            entity_id = person_key_manager.get_vault_entity_id()
            if not entity_id:
                return (False, "Unable to retrieve vault entity ID.")

            public_key = person_key_manager.get_public_key()
            if public_key is None:
                return (False, "No public key found on vault or locally.")
            
            # Validate the private key format
            try:
                serialization.load_pem_private_key(
                    key_content.encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )
            except Exception as e:
                self._logger.error(f"Invalid private key format: {e}", exc_info=True)
                return (False, f"Invalid private key format: {str(e)}")
            
            # Save the key
            key_dir = Util.get_key_dir(entity_id)
            os.makedirs(key_dir, exist_ok=True)
            
            private_key_path = os.path.join(key_dir, config.LOCAL_PRIVATE_KEY_FILENAME)
            
            # Backup existing key if present
            if os.path.exists(private_key_path):
                backup_path = private_key_path + '.backup'
                os.rename(private_key_path, backup_path)
                self._logger.info(f"Backed up existing private key to {backup_path}")
            
            # Write new key
            person_key_manager.save_key_locally(key_content.encode("utf-8"), private_key_path)
            
            # Set permissions
            os.chmod(private_key_path, 0o600)
            
            # Verify the key
            private_key = person_key_manager.read_private_key(private_key_path)
            if not Util.verify_key_pair_match(public_key, private_key):
                # Verification failed, remove the imported key
                # os.remove(private_key_path)
                return (False, "The imported private key does not match the public key on vault.")
            
            self._logger.info("Private key imported successfully from text")
            return (True, "Private key imported and verified successfully.")
            
        except Exception as e:
            self._logger.error(f"Error importing private key: {e}", exc_info=True)
            return (False, f"Error importing private key: {str(e)}")

    def get_private_key_path(self):
        """Get the path where private key is stored"""
        try:
            person_key_manager = PersonKeyManager(self._vault_client)
            private_key_path = os.path.join(Util.get_key_dir(
                person_key_manager.get_vault_entity_id()), config.LOCAL_PRIVATE_KEY_FILENAME)
            return private_key_path
        except Exception as e:
            self._logger.error(e, exc_info=True)
            raise ValueError(f"Failed to get private key path: {str(e)}")

    def get_private_key_content(self):
        """Get the private key content as string"""
        try:
            person_key_manager = PersonKeyManager(self._vault_client)
            key_content = person_key_manager.read_private_key(self.get_private_key_path())
            
            # Ensure it's a string, not bytes
            if isinstance(key_content, bytes):
                key_content = key_content.decode('utf-8')
            
            return key_content
        except Exception as e:
            self._logger.error(e, exc_info=True)
            raise ValueError(f"Failed to read private key: {str(e)}")
    
    def get_export_key_info(self):
        """Get all info needed for export: entity_id and key_content"""
        try:
            # Get entity ID
            entity_id = self._vault_client.entity_id
            
            # Get key content            
            key_content = self.get_private_key_content()
            
            return (entity_id, key_content)
        except Exception as e:
            self._logger.error(e, exc_info=True)
            raise ValueError(f"Failed to get export info: {str(e)}")

    # TODO: keep for future feature
    def review_shares(self):
        try:
            dataset_key_manager = DatasetKeyManager(self._vault_client)
            person_key_manager = PersonKeyManager(self._vault_client)
            encryptor = EncryptionClient(
                dataset_key_manager, person_key_manager)
            encryptor.list_shares()
        except Exception as e:
            self._logger.error(e, exc_info=True)

    # TODO: keep for future feature
    def revoke_access(self, dataset_name, requester_id):
        self._access_granter.revoke_access(requester_id, dataset_name)
        return True

    def get_entity_id(self):
        try:
            entity_id = self._vault_client.entity_id
            return (True, entity_id)
        except Exception as e:
            return (False, str(e))
    
    def get_request_info(self, requester_uuid, dataset_uuid):
        entity_success, entity_result = self.get_entity_name(requester_uuid)
        dataset_success, dataset_result = self.get_dataset_title(dataset_uuid)
        return (entity_success, entity_result, dataset_success, dataset_result)


    def get_entity_name(self, entity_id):
        try:
            return (True, self._vault_client.read_entity_by_id(entity_id))
        except Exception as e:
            return (False, str(e))
    
    def get_dataset_title(self, dataset_uuid):
        try:
            return (True, self._frdr_api_client.get_dataset_title(dataset_uuid))
        except Exception as e:
            return (False, str(e))
   
    def get_user_vault_id_from_frdr(self):
        try:
            return (True, self._frdr_api_client.get_user_vault_id_from_frdr())
        except Exception as e:
            return (False, str(e))

    def send_user_vault_id_to_frdr(self, user_vault_id):
        try:
            data = {"user_vault_id": user_vault_id}
            self._frdr_api_client.send_user_vault_id_to_frdr(data)
            return (True, None)
        except Exception as e:
            return (False, str(e))
class NoCommandError(Exception):
    pass

class ProgramExit(Exception):
    pass

def process_message(encryption_client, message):
    data = json.loads(message)
    command = data["command"]
    args = data.get("args", [])
    if hasattr(encryption_client, command):
        func = getattr(encryption_client, command)
        ret = func(*args)
        return {"result": ret}
    elif command == "Exit":
        raise ProgramExit
    else:
        raise NoCommandError(f"No such command : '{command}'")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    addr = "tcp://127.0.0.1:" + str(sys.argv[1])
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)
    socket.bind(addr)
    encryption_client = EncryptionClientGui()
    while True:
        message = socket.recv_string()
        try:
            ret = process_message(encryption_client, message)
            ret = json.dumps(ret)
            socket.send(ret.encode()) 
        except NoCommandError:
            continue
        except ProgramExit:
            break
