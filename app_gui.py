import webbrowser

from modules.PersonKeyManager import PersonKeyManager
from modules.EncryptionClient import EncryptionClient
from appdirs import AppDirs
import sys
import zerorpc
import os
from modules.VaultClient import VaultClient
from modules.AccessManager import AccessManager
from util.config_loader import config
import logging
from util.util import Util
import uuid
from modules.DatasetKeyManager import DatasetKeyManager
from modules.FRDRAPIClient import FRDRAPIClient


__version__ = config.VERSION
dirs = AppDirs(config.APP_NAME, config.APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)
tokenfile = os.path.join(dirs.user_data_dir, "vault_token")

class EncryptionClientGui(object):
    def __init__(self, tokenfile):
        self._tokenfile = tokenfile
        Util.get_logger("fdrd-encryption-client", 
                        log_level="info",
                        filepath=os.path.join(dirs.user_data_dir, "fdrd-encryption-client_log.txt"))
        self._logger = logging.getLogger("fdrd-encryption-client.gui")
        self._vault_client = VaultClient()
        self._frdr_api_client = FRDRAPIClient()
        # self._vault_client_pki = VaultClient()

    def login_oidc_google(self, hostname):
        try:
            self._logger.info("Log into Vault using oidc method with google acccount")
            self._vault_client.login(vault_addr=hostname,
                                     auth_method="oidc",
                                     oauth_type="google")          
            return (True, None)
        except Exception as e:
            self._logger.info(str(e))
            return (False, str(e))
    
    def login_oidc_globus(self, hostname, hostname_pki):
        try:
            self._logger.info("Log into Vault using oidc method with globus acccount") 
            self._vault_client.login(vault_addr=hostname,
                                     auth_method="oidc")  
            # self._vault_client_pki.login(vault_addr=hostname_pki, 
            #                          auth_method="oidc")           
            return (True, None)
        except Exception as e:
            self._logger.info(str(e))
            return (False, str(e))
    
    def login_frdr_api_globus(self, base_url):
        try:
            self._logger.info("Login with globus acccount for FRDR REST API usage") 
            self._frdr_api_client.login(base_url=base_url)    
            return (True, None)
        except Exception as e:
            self._logger.info(str(e))
            return (False, str(e))

    def logout(self):
        try:
            self._vault_client.logout()
            # webbrowser.open("https://auth.globus.org/v2/web/logout")
            self._logger.info("Log out successfully")
            return (True, None)
        except Exception as e:
            self._logger.error(str(e))
            return (False, str(e))

    def encrypt(self, input_path, output_path):
        try:
            self._logger.info("Encrypt files in the path {}".format(input_path))
            dataset_uuid = str(uuid.uuid4()) 
            dataset_key_manager = DatasetKeyManager(self._vault_client)
            person_key_manager = PersonKeyManager(self._vault_client)
            encryptor = EncryptionClient(dataset_key_manager, person_key_manager, input_path, output_path)
            bag_path = encryptor.encrypt(dataset_uuid)
            return (True, bag_path)
        except Exception as e:
            self._logger.info(str(e))
            return (False, str(e))

    def decrypt(self, input_path, output_path, url):
        try:
            self._logger.info("Decrypt files in the path {}".format(input_path))
            dataset_key_manager = DatasetKeyManager(self._vault_client)
            person_key_manager = PersonKeyManager(self._vault_client)
            encryptor = EncryptionClient(dataset_key_manager, person_key_manager, input_path, output_path)
            encryptor.decrypt(url)
            return (True, None)
        except Exception as e:
            self._logger.info(str(e))
            return (False, str(e))

    def grant_access(self, dataset_uuid, requester_uuid, expire_date):
        try:
            dataset_key_manager = DatasetKeyManager(self._vault_client)
            person_key_manager = PersonKeyManager(self._vault_client)
            encryptor = EncryptionClient(dataset_key_manager, person_key_manager)
            encryptor.grant_access(requester_uuid, dataset_uuid, expire_date) 
            data = {"expires": expire_date, "vault_dataset_id": dataset_uuid, "vault_requester_id": requester_uuid}
            self._frdr_api_client.update_requestitem(data)
            return (True, None)
        except Exception as e:
            return (False, str(e))

    def create_access_granter(self, username, password, vault_token, hostname):
        try:
            vault_client = VaultClient(hostname, username, password, tokenfile, vault_token)
            # TODO: add another method to set self._access_granter to null when the review window is closed
            access_granter = AccessManager(vault_client)
            self._access_granter = access_granter
            return (True, None)
        except Exception as e:
            return (False, str(e))

    def review_shares(self):
        try:
            return self._access_granter.list_members()
        except Exception as e:
            self._logger.error(e, exc_info=True)

    def revoke_access(self, dataset_name, requester_id):
        self._access_granter.revoke_access(requester_id, dataset_name)
        return True

    def set_input_path(self, input_path):
        self._logger.info("Setting input path.")
        self._input_path = input_path
    
    def unset_input_path(self):
        self._logger.info("Clearing input path.")
        self._input_path = None
    
    def get_entity_name(self, entity_id):
        try:
            return (True, self._vault_client.read_entity_by_id(entity_id))
        except Exception as e:
            return (False, str(e))

    def get_entity_id(self):
        try:
            entity_id = self._vault_client.entity_id
            person_key_manager = PersonKeyManager(self._vault_client)
            # make sure there is a public key saved on Vault for the requester
            person_key_manager.create_or_retrieve_public_key()
            return (True, entity_id)
        except Exception as e:
            return (False, str(e))

    def get_auth_url(self, hostname, hostname_pki):
        return (self._vault_client.get_oidc_auth_url(hostname), None)
    
    def login_oidc_temp(self, auth_url):
        try:
            self._vault_client.login_oidc_temp(auth_url)
            return (True, None)
        except Exception as e:
            return (False, str(e)) 

if __name__ == "__main__":
    s = zerorpc.Server(EncryptionClientGui(tokenfile=tokenfile))
    s.bind("tcp://127.0.0.1:" + str(sys.argv[1]))
    s.run()