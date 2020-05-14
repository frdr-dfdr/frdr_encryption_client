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
        self._hvac_client = vault_client.hvac_client
        self._key_ring_name = key_ring_name
        self._key = None
        self._key_ciphertext = None

    def generate_key(self):
        self._enable_transit_engine()
        self._create_transit_engine_key_ring(self._key_ring_name)
        key_plaintext, key_ciphertext = self._generate_data_key(self._key_ring_name)
        self._key = base64_to_byte(key_plaintext)
        self._key_ciphertext = key_ciphertext

    def save_key(self, path):
        self._hvac_client.secrets.kv.v2.create_or_update_secret(path=path, secret=dict(ciphertext=self._key_ciphertext))

    def read_key(self, path):
        key_ciphertext = self._retrive_key_from_vault(path)
        key_plaintext = self._decrypt_data_key_on_vault(self._key_ring_name, key_ciphertext)
        self._key = base64_to_byte(key_plaintext)

    @property
    def key(self):
        if self._key is None:
            self.generate_key()
        return self._key

    def _retrive_key_from_vault(self, path):
        read_secret_response = self._hvac_client.secrets.kv.v2.read_secret_version(path=path)
        key_ciphertext = read_secret_response['data']['data']['ciphertext']
        return key_ciphertext
    
    def _decrypt_data_key_on_vault(self, name, ciphertext):
        decrypt_data_response = self._hvac_client.secrets.transit.decrypt_data(name=name, ciphertext=ciphertext,)
        key_plaintext = decrypt_data_response['data']['plaintext']
        return key_plaintext

    def _enable_transit_engine(self):
        try:
            self._hvac_client.sys.enable_secrets_engine(backend_type='transit')
        except hvac.exceptions.InvalidRequest as e:
            pass
    
    def _create_transit_engine_key_ring(self, name):
        self._hvac_client.secrets.transit.create_key(name=name)

    def _generate_data_key(self, name, key_type="plaintext"):
        gen_key_response = self._hvac_client.secrets.transit.generate_data_key(name=name, key_type=key_type,)
        key_plaintext = gen_key_response['data']['plaintext']
        key_ciphertext = gen_key_response['data']['ciphertext']
        return (key_plaintext, key_ciphertext)    
