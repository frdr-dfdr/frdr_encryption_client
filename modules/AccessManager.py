from modules.VaultClient import VaultClient
import json

class AccessManager(object):
    # TODO: add logger in this class
    def __init__(self, vault_client):
        self._vault_client = vault_client
        self._depositor_entity_id = self._vault_client.entity_id
    def grant_access(self, requester_entity_id, dataset_id):
        group_name = "_".join((self._depositor_entity_id, dataset_id, "share_group"))
        self._add_member_to_group(group_name, requester_entity_id)
    
    def _add_member_to_group(self, group_name, requester_entity_id):
        read_group_response = self._vault_client.read_group_by_name(group_name)
        member_entity_ids = read_group_response["data"]["member_entity_ids"]
        member_entity_ids.append(requester_entity_id)
        policies = read_group_response["data"]["policies"]
        self._vault_client.create_or_update_group_by_name(group_name, policies, member_entity_ids)
    
    def revoke_access(self, requester_entity_id, dataset_id):
        group_name = "_".join((self._depositor_entity_id, dataset_id, "share_group"))
        self._remove_member_from_group(group_name, requester_entity_id)

    def _remove_member_from_group(self, group_name, requester_entity_id):
        read_group_response = self._vault_client.read_group_by_name(group_name)
        member_entity_ids = read_group_response["data"]["member_entity_ids"]
        member_entity_ids.remove(requester_entity_id)
        policies = read_group_response["data"]["policies"]
        self._vault_client.create_or_update_group_by_name(group_name, policies, member_entity_ids)

    def list_members(self):
        members = {}
        members["entity_id"] = self._depositor_entity_id
        members["data"] = []
        depositor_datasets = self._list_datasets()
        for each_dataset_id in depositor_datasets:
            group_name = "_".join((self._depositor_entity_id, each_dataset_id, "share_group"))
            each_dataset_members = {}
            each_dataset_members["dataset_id"] = each_dataset_id
            each_dataset_members["members"] = []
            for each_member_id in self._list_members_per_group(group_name):
                each_member_name = self._vault_client.read_entity_by_id(each_member_id)
                each_member = {"entity_id": each_member_id, "entity_name": each_member_name}
                each_dataset_members["members"].append(each_member)
            members["data"].append(each_dataset_members)
        return json.dumps(members)
    
    def _list_members_per_group(self, group_name):
        read_group_response = self._vault_client.read_group_by_name(group_name)
        member_entity_ids = read_group_response["data"]["member_entity_ids"]
        return member_entity_ids

    def _list_datasets(self):        
        return self._vault_client.list_secrets(self._depositor_entity_id)