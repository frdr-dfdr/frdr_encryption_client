from shutil import ExecError
import nacl
import hvac
import logging
from util.util import Util
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

Util.get_logger("frdr-crypto.key-manager")
class KeyManagementLocal(object):
    def __init__(self):
        self._key = None
        self._logger = logging.getLogger("frdr-crypto.key-mamanger.local")
    
    def generate_key(self):
        self._key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
        self._logger.info("Key is generated using python nacl package.")
    
    def save_key(self, filename):
        with open(filename, 'wb') as f:
            f.write(self._key)
        self._logger.info("Key is saved to local path {}".format(filename))
    
    def read_key(self, filename):
        with open(filename, "rb") as f:
            self._key = f.read()
        self._logger.info("key is read from local path {}".format(filename))

    @property
    def key(self):
        if self._key is None:
            self.generate_key()
        return self._key

class KeyManagementVault(object):
    def __init__(self, vault_client, key_ring_name=None):
        self._logger = logging.getLogger("frdr-crypto.key-mamanger.vault")
        self._vault_client = vault_client
        self._key_ring_name = self._vault_client.entity_id #key_ring_name is the user_entity_id
        self._key = None
        self._key_encrypted = None

    def generate_key(self):
        # added create encryption key permission for frdr-user policy
        try:
            print(self._vault_client._vault_token)
            self._vault_client.create_transit_engine_key_ring(self._key_ring_name, mount_point="transit/dataset")
        except Exception as e:
            print (str(e))
        # added generate data key permission for frdr-user policy
        key_plaintext = self._vault_client.generate_data_key(self._key_ring_name, mount_point="transit/dataset")
        self._key = Util.base64_to_byte(key_plaintext) 
        self._logger.info("Key is generated by vault transit secrets engine.")

    def encrypt_key(self, user_public_key):
        public_key = serialization.load_pem_public_key(
                user_public_key.encode(),
                backend=default_backend())
        key_encrypted = public_key.encrypt(
                                    self._key,
                                    padding.OAEP(
                                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                        algorithm=hashes.SHA256(),
                                        label=None
                                    ))
        self._key_encrypted = Util.byte_to_base64(key_encrypted)
        # TODO: delete later
        print ("Encrypted key is:" + self._key_encrypted)


    def save_key(self, path):
        self._vault_client.save_key_to_vault(path, self._key_encrypted)
        self._logger.info("Key is saved to vault")

    def read_key(self, path):
        self._key_encrypted = self._vault_client.retrive_key_from_vault(path)
        self._logger.info("key is read from vault")

    def decrypt_key(self, user_private_key):
        self._key = user_private_key.decrypt(
                                Util.base64_to_byte(self._key_encrypted),
                                padding.OAEP(
                                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                    algorithm=hashes.SHA256(),
                                    label=None
                                )
                            )

    def get_vault_entity_id(self):
        return self._vault_client.entity_id

    @property
    def key(self):
        if self._key is None:
            self.generate_key()
        return self._key