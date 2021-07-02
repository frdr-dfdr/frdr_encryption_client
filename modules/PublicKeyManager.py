import nacl
import hvac
import logging
from util.util import Util

Util.get_logger("frdr-crypto.public-key-manager")

class PublicKeyManager(object):
    def __init__(self, vault_client):
        self._logger = logging.getLogger("frdr-crypto.public-key-mamanger.vault")
        self._vault_client = vault_client
        self._key_name = self._vault_client.entity_id #key_ring_name is the user entity id

    def create_key_pair(self):
        self._vault_client.create_transit_engine_key_ring(name=self._key_name, 
                                                          mount_point="transit/keypair",
                                                          exportable=True,
                                                          key_type="rsa-2048")

    def get_public_key(self, user_entity_id):
        public_key = self._vault_client.read_transit_key_rsa(name=user_entity_id, mount_point="transit/keypair")
        self._logger.info("Get public key for user {}".format(user_entity_id))
        return public_key

    def get_private_key(self):
        private_key = self._vault_client.export_transit_key_rsa(name=self._key_name, mount_point="transit/keypair")
        self._logger.info("Get private key for user {}".format(self._key_name))
        return private_key
    
    def get_vault_entity_id(self):
        return self._vault_client.entity_id


