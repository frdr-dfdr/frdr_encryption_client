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


class EncryptionClientGui(object):
    def __init__(self):
        Util.get_logger("frdr-encryption-client",
                        log_level="info",
                        filepath=os.path.join(dirs.user_data_dir, config.APP_LOG_FILENAME))
        self._logger = logging.getLogger("frdr-encryption-client.gui")
        self._vault_client = VaultClient()
        self._frdr_api_client = FRDRAPIClient()
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

    def login_frdr_api_globus(self, success_msg, base_url=None):
        try:
            self._logger.info(
                "Login with globus acccount for FRDR REST API usage")
            if base_url is None:
                base_url = config.FRDR_API_BASE_URL
            self._frdr_api_client.login(base_url=base_url, success_msg=success_msg)
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
        try:
            self._logger.info(
                "Encrypt files in the path {}".format(input_path))
            dataset_uuid = str(uuid.uuid4())
            dataset_key_manager = DatasetKeyManager(self._vault_client)
            person_key_manager = PersonKeyManager(self._vault_client)
            encryptor = EncryptionClient(
                dataset_key_manager, person_key_manager, input_path, output_path)
            bag_path = encryptor.encrypt(dataset_uuid)
            return (True, bag_path)
        except Exception as e:
            self._logger.info(str(e))
            return (False, str(e))

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

    def grant_access(self, dataset_uuid, requester_uuid, expire_date):
        try:
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


if __name__ == "__main__":
    s = zerorpc.Server(EncryptionClientGui())
    s.bind("tcp://127.0.0.1:" + str(sys.argv[1]))
    s.run()
