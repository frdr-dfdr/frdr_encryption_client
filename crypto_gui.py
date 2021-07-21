from appdirs import AppDirs
import sys
import zerorpc
import os
from tempfile import mkstemp, gettempdir
from shutil import move
import json
from modules.VaultClient import VaultClient
from modules.AccessManager import AccessManager
from config import app_config
import logging
from util.util import Util
import uuid
from modules.DatasetKeyManager import DatasetKeyManager


__version__ = app_config.VERSION
dirs = AppDirs(app_config.APP_NAME, app_config.APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)
tokenfile = os.path.join(dirs.user_data_dir, "vault_token")

class CryptoGui(object):
    def __init__(self, tokenfile):
        self._tokenfile = tokenfile
        Util.get_logger("fdrd-encryption-client", 
                        log_level="info",
                        filepath=os.path.join(dirs.user_data_dir, "fdrd-encryption-client_log.txt"))
        self._logger = logging.getLogger("fdrd-encryption-client.gui")
        self._vault_client = VaultClient()
        self._vault_client_pki = VaultClient()

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
                                     auth_method="oidc",
                                     oauth_type="globus")  
            self._vault_client_pki.login(vault_addr=hostname_pki, 
                                     auth_method="oidc")           
            return (True, None)
        except Exception as e:
            self._logger.info(str(e))
            return (False, str(e))

    def logout(self):
        try:
            self._vault_client.logout()
            self._vault_client_pki.logout()
            self._logger.info("Log out successfully")
            return (True, None)
        except Exception as e:
            self._logger.error(str(e))
            return (False, str(e))

    def encrypt(self, username, password, vault_token, hostname, output_path):
        try:
            self._logger.info("Encrypt files in the path {}".format(self._input_path))
            vault_client = VaultClient(hostname, username, password, tokenfile, vault_token)
            dataset_name = str(uuid.uuid4()) 
            key_manager = DatasetKeyManager(vault_client, dataset_name)
            arguments = {"--input": self._input_path, 
                        "--output": output_path,
                        "--username": username,
                        "--password": password,
                        "--vault": hostname,
                        "--encrypt": True}
            encryptor = EncryptionClient(key_manager, self._logger, dataset_name)
            bag_path = encryptor.encrypt()
            return (True, bag_path)
        except Exception as e:
            self._logger.info(str(e))
            return (False, str(e))

    def decrypt(self, username, password, vault_token, hostname, url, output_path):
        try:
            self._logger.info("Decrypt files in the path {}".format(self._input_path))
            vault_client = VaultClient(hostname, username, password, tokenfile, vault_token)
            dataset_name = url.split("/")[-1]
            key_manager = DatasetKeyManager(vault_client, dataset_name)
            arguments = {"--input": self._input_path, 
                        "--output": output_path,
                        "--username": username,
                        "--password": password, 
                        "--vault": hostname,
                        "--url": url,
                        "--decrypt": True,
                        "--encrypt": False}
            encryptor = EncryptionClient(key_manager, self._logger, dataset_name)
            encryptor.decrypt()
            return (True, None)
        except Exception as e:
            return (False, str(e))

    def grant_access(self, username, password, vault_token, hostname, dataset_name, requester_id, expiry_date):
        try:
            vault_client = VaultClient(hostname, username, password, tokenfile, vault_token)
            access_granter = AccessManager(vault_client)
            access_granter.grant_access(requester_id, dataset_name, expiry_date)
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
    
    def get_entity_name(self, username, password, vault_token, hostname, entity_id):
        try:
            vault_client = VaultClient(hostname, username, password, tokenfile, vault_token)
            return (True, vault_client.read_entity_by_id(entity_id))
        except Exception as e:
            return (False, str(e))

    def get_entity_id(self, username, password, vault_token, hostname):
        try:
            vault_client = VaultClient(hostname, username, password, tokenfile, vault_token)
            return (True, vault_client.entity_id)
        except Exception as e:
            return (False, str(e))

if __name__ == "__main__":
    s = zerorpc.Server(CryptoGui(tokenfile=tokenfile))
    s.bind("tcp://127.0.0.1:" + str(sys.argv[1]))
    s.run()