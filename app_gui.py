from ctypes import c_char_p, c_bool
import datetime
from multiprocessing import Process, Manager
import multiprocessing
import webbrowser
from modules.PersonKeyManager import PersonKeyManager
from modules.EncryptionClient import EncryptionClient
from appdirs import AppDirs
import sys
import zerorpc
import os
from modules.VaultClient import VaultClient
from util.config_loader import config
import logging
from util.util import Util
import uuid
from modules.DatasetKeyManager import DatasetKeyManager
from modules.FRDRAPIClient import FRDRAPIClient

__version__ = config.VERSION
dirs = AppDirs(config.APP_NAME, config.APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)

def encrypt_in_process(input_path, output_path, vault_client_token, 
                       vault_client_entity_id, vault_client_addr, 
                       return_message, return_successful):
    try:
        Util.get_logger("frdr-encryption-client",
                        log_level="info",
                        filepath=os.path.join(dirs.user_data_dir, config.APP_LOG_FILENAME))
        logger = logging.getLogger("frdr-encryption-client.gui.encrypt")
        logger.info("Encrypt files in the path {}".format(input_path))
        with open(os.path.join(dirs.user_data_dir, "pid"), 'w') as f:
            f.write(str(os.getpid()))
        dataset_uuid = str(uuid.uuid4())
        vault_client = VaultClient(token=vault_client_token, entity_id=vault_client_entity_id, url=vault_client_addr)
        dataset_key_manager = DatasetKeyManager(vault_client)
        person_key_manager = PersonKeyManager(vault_client)
        encryptor = EncryptionClient(
            dataset_key_manager, person_key_manager, input_path, output_path)
        bag_path = encryptor.encrypt(dataset_uuid)
        return_message.value = bag_path
        return_successful.value = True
    except Exception as e:
        return_message.value = str(e)
        return_successful.value = False
        logger.info(e, exc_info=True)

class EncryptionClientGui(object):
    def __init__(self):
        Util.get_logger("frdr-encryption-client",
                        log_level="info",
                        filepath=os.path.join(dirs.user_data_dir, config.APP_LOG_FILENAME))
        self._logger = logging.getLogger("frdr-encryption-client.gui")
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

    def login_oidc_globus(self, hostname, hostname_pki, success_msg):
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
        message = manager.Value(c_char_p, "Terminated")
        successful = manager.Value(c_bool, False)
        p = Process(target=encrypt_in_process, args=(input_path, output_path, self._vault_client.token, self._vault_client.entity_id, self._vault_client.url, message, successful))
        p.start()
        p.join()
        return (successful.value, message.value)
    
    def cleanup(self):
        self._logger.info("Encryption has been terminated by the user.")

    def decrypt(self, input_path, output_path, url):
        try:
            self._logger.info(
                "Decrypt files in the path {}".format(input_path))
            dataset_key_manager = DatasetKeyManager(self._vault_client)
            person_key_manager = PersonKeyManager(self._vault_client)
            encryptor = EncryptionClient(
                dataset_key_manager, person_key_manager, input_path, output_path)
            encryptor.decrypt(url)
            return (True, None)
        except Exception as e:
            self._logger.info(str(e))
            return (False, str(e))

    def grant_access(self, dataset_uuid, requester_uuid, expire_date=None):
        try:
            if expire_date is None:
                expire_date = (datetime.date.today() + datetime.timedelta(days=30*6)).strftime("%Y-%m-%d")
            
            dataset_key_manager = DatasetKeyManager(self._vault_client)
            person_key_manager = PersonKeyManager(self._vault_client)
            encryptor = EncryptionClient(
                dataset_key_manager, person_key_manager)
            encryptor.grant_access(requester_uuid, dataset_uuid, expire_date)
            data = {"expires": expire_date, "vault_dataset_id": dataset_uuid,
                    "vault_requester_id": requester_uuid}
            self._frdr_api_client.update_requestitem(data)
            return (True, None)
        except Exception as e:
            self._logger.error(e, exc_info=True)
            return (False, str(e))

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
            person_key_manager = PersonKeyManager(self._vault_client)
            # make sure there is a public key saved on Vault for the requester
            person_key_manager.create_or_retrieve_public_key()
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



if __name__ == "__main__":
    multiprocessing.freeze_support()
    s = zerorpc.Server(EncryptionClientGui())
    s.bind("tcp://127.0.0.1:" + str(sys.argv[1]))
    s.run()
