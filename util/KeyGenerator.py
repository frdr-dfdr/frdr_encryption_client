import nacl
import hvac
from util.helper import base64_to_byte

class KeyManagementLocal(object):
    def __init__(self):
        self._key = None
    
    def generate_key(self):
        self._key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    
    def save_key(self, filename):
        with open(filename, 'wb') as f:
            f.write(self._key)
    
    def read_key(self, filename):
        with open(filename, "rb") as f:
            self._key = f.read()
    
    @property
    def key(self):
        if self._key is None:
            self.generate_key()
        return self._key

class KeyManagementVault(object):
    def __init__(self, vault_client, key_ring_name):
        self._hvac_client = vault_client
        self._key_ring_name = key_ring_name
        self._key = None
        self._key_ciphertext = None

    def generate_key(self):
        # enable transit engine should be done by vault admin
        # self._hvac_client.enable_transit_engine()
        # added create encryption key permission for frdr-user policy
        self._hvac_client.create_transit_engine_key_ring(self._key_ring_name)
        # added generate data key permission for frdr-user policy
        key_plaintext, key_ciphertext = self._hvac_client.generate_data_key(self._key_ring_name)
        self._key = base64_to_byte(key_plaintext)
        self._key_ciphertext = key_ciphertext

    def save_key(self, path):
        self._hvac_client.save_key_to_vault(path, self._key_ciphertext)

    def read_key(self, path):
        key_ciphertext = self._hvac_client.retrive_key_from_vault(path)
         # added decrypt data permission for frdr-user policy
        key_plaintext = self._hvac_client.decrypt_data_key(self._key_ring_name, key_ciphertext)
        self._key = base64_to_byte(key_plaintext)

    def get_vault_entity_id(self):
        return self._hvac_client.entity_id

    @property
    def key(self):
        if self._key is None:
            self.generate_key()
        return self._key