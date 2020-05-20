from util.VaultClient import VaultClient
class AccessGranter(object):
    def __init__(self, vault_client):
        self._vault_client = vault_client
        self._depositor_entity_id = self._vault_client.entity_id
    def grant_access(self, requester_entity_id, dataset_id):
        group_name = self._create_share_group(dataset_id)
        policy_name = self._create_share_policy(dataset_id) 
        self._add_policy_to_group(group_name, policy_name)
        self._add_member_to_group(group_name, requester_entity_id)
        
    def _create_share_policy(self, dataset_id):
        policy_string = f="""
            path "secret/data/{user_entity_id}/{dataset_id}" {{
                capabilities = [ "read", "list", "delete"]
            }}
        """.format(user_entity_id=self._depositor_entity_id, dataset_id=dataset_id)
        policy_name = "_".join((self._depositor_entity_id, dataset_id, "share_policy"))
        if self._vault_client.create_policy(policy_name, policy_string):
            return policy_name
        else:
            #TODO: raise error or return false
            raise RuntimeError
        
    def _create_share_group(self, dataset_id):
        group_name = "_".join((self._depositor_entity_id, dataset_id, "share_group"))
        response = self._vault_client.create_or_update_group_by_name(group_name=group_name)
        try:
            group_name = response["data"]["name"]
        except:
            pass
        return group_name
    
    def _add_member_to_group(self, group_name, requester_entity_id):
        read_group_response = self._vault_client.read_group_by_name(group_name)
        member_entity_ids = read_group_response["data"]["member_entity_ids"]
        member_entity_ids.append(requester_entity_id)
        policies = read_group_response["data"]["policies"]
        self._vault_client.create_or_update_group_by_name(group_name, policies, member_entity_ids)
    
    def _add_policy_to_group(self, group_name, policy_name):
        self._vault_client.create_or_update_group_by_name(group_name=group_name, 
                                                          policy_name=policy_name)