import hvac
class VaultClient(object):
    def __init__(self, vault_addr, vault_token=None):
        # TODO: change to vault token path
        self._vault_addr = vault_addr
        self._vault_token = vault_token
        try:
            self.hvac_client = hvac.Client(
                url=self._vault_addr, 
                token=self._vault_token
                )
            assert self.hvac_client.is_authenticated(), \
                   'Failed to authenticate with Vault, please check your Vault server URL and Vault token!'
        except AssertionError as error:
            # TODO: log error
            pass
        #TODO: log connected to vault successfully
    
    def enable_transit_engine(self):
        try:
            self.hvac_client.sys.enable_secrets_engine(backend_type='transit')
        except hvac.exceptions.InvalidRequest as e:
            pass
    def create_transit_engine_key_ring(self, name):
        self.hvac_client.secrets.transit.create_key(name=name)

    def generate_data_key(self, name, key_type="plaintext"):
        gen_key_response = self.hvac_client.secrets.transit.generate_data_key(name=name, key_type=key_type,)
        key_plaintext = gen_key_response['data']['plaintext']
        key_ciphertext = gen_key_response['data']['ciphertext']
        return (key_plaintext, key_ciphertext)

    def decrypt_key(self, name, ciphertext):
        decrypt_data_response = self.hvac_client.secrets.transit.decrypt_data(name=name, ciphertext=ciphertext,)
        key_plaintext = decrypt_data_response['data']['plaintext']
        return key_plaintext

    def save_key_to_vault(self, path, key):
        self.hvac_client.secrets.kv.v2.create_or_update_secret(path=path, secret=dict(ciphertext=key))
    
    def retrive_key_from_vault(self, path):
        read_secret_response = self.hvac_client.secrets.kv.v2.read_secret_version(path=path)
        key_ciphertext = read_secret_response['data']['data']['ciphertext']
        return key_ciphertext
