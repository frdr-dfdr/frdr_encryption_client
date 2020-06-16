from appdirs import AppDirs
import sys
import zerorpc
import os
from tempfile import mkstemp, gettempdir
from shutil import move
import json
from modules.VaultClient import VaultClient
from modules.AccessGranter import AccessGranter
from util import constants
import logging
from util.util import Util
import uuid
from crypto import Cryptor
from modules.KeyGenerator import KeyManagementVault


__version__ = constants.VERSION
dirs = AppDirs(constants.APP_NAME, constants.APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)
tokenfile = os.path.join(dirs.user_data_dir, "vault_token")

class CryptoGui(object):
    def __init__(self, tokenfile):
        self._tokenfile = tokenfile
        Util.get_logger("frdr-crypto", 
                        log_level="info",
                        filepath=os.path.join(dirs.user_data_dir, "frdr-crypto_log.txt"))
        self._logger = logging.getLogger("frdr-crypto.gui")

    def get_token(self, username, password, hostname):
        self._logger.info("Get token from GUI.")
        vault_client = VaultClient(hostname, username, password, tokenfile)
        login_status = vault_client.login(username, password)
        if login_status:
            return "Token obtained."
        else:
            return "Unable to obtain token. Verify your credentials and Vault URL."

    def encrypt(self, username, password, hostname):
        self._logger.info("Encrypt files in the path {}".format(self._input_path))
        vault_client = VaultClient(hostname, username, password, tokenfile)
        dataset_name = str(uuid.uuid4()) 
        key_manager = KeyManagementVault(vault_client, dataset_name)
        arguments = {"--input": self._input_path, 
                     "--output": None,
                     "--username": username,
                     "--password": password, 
                     "--vault": hostname,
                     "--encrypt": True}
        self._logger.info(arguments)
        encryptor = Cryptor(arguments, key_manager, self._logger, dataset_name)
        encryptor.encrypt()
        return True

    def decrypt(self, username, password, hostname, url):
        self._logger.info("Decrypt files in the path {}".format(self._input_path))
        vault_client = VaultClient(hostname, username, password, tokenfile)
        dataset_name = url.split("/")[-1]
        key_manager = KeyManagementVault(vault_client, dataset_name)
        arguments = {"--input": self._input_path, 
                     "--output": None,
                     "--username": username,
                     "--password": password, 
                     "--vault": hostname,
                     "--url": url,
                     "--decrypt": True,
                     "--encrypt": False}
        self._logger.info(arguments)
        encryptor = Cryptor(arguments, key_manager, self._logger, dataset_name)
        encryptor.decrypt()
        return True

    def grant_access(self, username, password, hostname, dataset_name, requester_id):
        vault_client = VaultClient(hostname, username, password, tokenfile)
        access_granter = AccessGranter(vault_client)
        access_granter.grant_access(requester_id, dataset_name)
        return True

    def set_input_path(self, input_path):
        self._logger.info("Setting input path.")
        self._input_path = input_path
    
    def get_entity_name(self, username, password, hostname, entity_id):
        vault_client = VaultClient(hostname, username, password, tokenfile)
        return vault_client.read_entity_by_id(entity_id)

if __name__ == "__main__":
    s = zerorpc.Server(CryptoGui(tokenfile=tokenfile))
    s.bind("tcp://127.0.0.1:" + str(sys.argv[1]))
    s.run()