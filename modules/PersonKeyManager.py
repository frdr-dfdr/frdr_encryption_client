import os
import logging
from util.util import Util
from config import person_key_server_config
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography import x509

class PersonKeyManager(object):
    def __init__(self, vault_client):
        self._logger = logging.getLogger("fdrd-encryption-client.person-key-manager.vault")
        self._vault_client = vault_client
        self._public_key = None

    def create_key_pair(self):
        self._vault_client.create_transit_engine_key_ring(name=self._key_name, 
                                                          mount_point="transit/keypair",
                                                          exportable=True,
                                                          key_type="rsa-2048")

    def generate_certificate(self):
        certificate, private_key_str = self._vault_client.generate_certificate(
            name=person_key_server_config.VAULT_GENERATE_CERT_ROLE_NAME,
            common_name=person_key_server_config.VAULT_GENERATE_CERT_COMMON_NAME,
            mount_point=person_key_server_config.VAULT_GENERATE_CERT_MOUNT_NAME
        )
        private_key = private_key_str.encode()
        return (certificate, private_key)
    
    def save_key_locally(self, key, filename):
        with open(filename, 'wb') as f:
            f.write(key)
        self._logger.info("Key is saved to local path {}".format(filename))
    
    def read_private_key(self, filename):
        with open(filename, "rb") as f:
            private_key = f.read()
        self._logger.info("Private key is read from local path {}".format(filename))
        return private_key

    def extract_public_key_from_cert(self, cert):
        certificate = x509.load_pem_x509_certificate(
            cert.encode(),
            backend=default_backend()
        )
        public_key = certificate.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_key

    def save_public_key_to_vault(self, public_key):
        path = "/".join([person_key_server_config.VAULT_PUBLIC_KEY_PATH, self.get_vault_entity_id()])
        if isinstance(public_key, bytes):
            public_key = Util.byte_to_base64(public_key)
        self._vault_client.save_key_to_vault(path, public_key)

    def read_public_key_from_vault(self, user_entity_id):
        try:
            path = "/".join([person_key_server_config.VAULT_PUBLIC_KEY_PATH, user_entity_id])
            return self._vault_client.retrive_key_from_vault(path)
        except Exception as e:
            self._logger.error("Falied to read public key from Vault. {}".format(e))
            return None
    
    def get_vault_entity_id(self):
        return self._vault_client.entity_id

    def create_or_retrieve_public_key(self):
        public_key_on_vault = self.read_public_key_from_vault(self.get_vault_entity_id())
        if public_key_on_vault is None:
            self._logger.info("No public key is saved on Vault for the current user, generating a pair of public and private key")
            cert, private_key = self.generate_certificate()
            private_key_path = os.path.join(Util.get_key_dir(self.get_vault_entity_id()), person_key_server_config.LOCAL_PRIVATE_KEY_FILENAME)
            self.save_key_locally(private_key, private_key_path)
            public_key = self.extract_public_key_from_cert(cert)
            public_key_path = os.path.join(Util.get_key_dir(self.get_vault_entity_id()), person_key_server_config.LOCAL_PUBLIC_KEY_FILENAME)
            self.save_key_locally(public_key, public_key_path)
            self.save_public_key_to_vault(public_key)
            return public_key
        else:
            return public_key_on_vault

    @property
    def my_public_key(self):
        if self._public_key is None:
            self._public_key = self.create_or_retrieve_public_key()
        return self._public_key

