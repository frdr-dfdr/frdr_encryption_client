import nacl
import hvac
from util.util import Util

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
        self._vault_client = vault_client
        self._key_ring_name = key_ring_name #key_ring_name is the dataset_id
        self._key = None
        self._key_ciphertext = None
        self._dataset_access_policy_name = "_".join((self._vault_client.entity_id, self._key_ring_name, "share_policy"))
        self._dataset_access_group_name = "_".join((self._vault_client.entity_id, self._key_ring_name, "share_group"))

    def generate_key(self):
        # enable transit engine should be done by vault admin
        # self._vault_client.enable_transit_engine()
        # added create encryption key permission for frdr-user policy
        self._vault_client.create_transit_engine_key_ring(self._key_ring_name)
        # added generate data key permission for frdr-user policy
        key_plaintext, key_ciphertext = self._vault_client.generate_data_key(self._key_ring_name)
        self._key = Util.base64_to_byte(key_plaintext)
        self._key_ciphertext = key_ciphertext

    def save_key(self, path):
        self._vault_client.save_key_to_vault(path, self._key_ciphertext)

    def read_key(self, path):
        key_ciphertext = self._vault_client.retrive_key_from_vault(path)
         # added decrypt data permission for frdr-user policy
        key_plaintext = self._vault_client.decrypt_data_key(self._key_ring_name, key_ciphertext)
        self._key = Util.base64_to_byte(key_plaintext)

    def get_vault_entity_id(self):
        return self._vault_client.entity_id

    def create_access_policy_and_group(self):
        if not self._dataset_access_policy_exists():
            self._create_dataset_access_policy()
        if not self._dataset_access_group_exists():
            self._create_dataset_access_group()

    def _dataset_access_policy_exists(self):
        try:
            self._vault_client.read_policy(self._dataset_access_policy_name)
        except hvac.exceptions.InvalidPath:
            print ("Policy does not exist.")
            return False
        else:
            print ("Policy already exists.")
            return False

    def _create_dataset_access_policy(self):
        policy_string = """
            path "secret/data/{user_entity_id}/{dataset_id}" {{
                capabilities = [ "read", "list", "delete"]
            }}
        """.format(user_entity_id=self._vault_client.entity_id, dataset_id=self._key_ring_name)
        if self._vault_client.create_policy(self._dataset_access_policy_name, policy_string):
            return True
        else:
            #TODO: raise error or return false
            raise RuntimeError

    def _dataset_access_group_exists(self):
        try:
            self._vault_client.read_group_by_name(self._dataset_access_group_name)
        except hvac.exceptions.InvalidPath:
            print ("Group does not exist")
            return False
        print ("Group already exists.")
        return True

    def _create_dataset_access_group(self):
        print ("create group")
        response = self._vault_client.create_or_update_group_by_name(group_name=self._dataset_access_group_name,
                                                                     policy_name=self._dataset_access_policy_name)
        # TODO: check the return value
        try:
            group_name = response["data"]["name"]
        except:
            pass
        return group_name

    @property
    def key(self):
        if self._key is None:
            self.generate_key()
        return self._key