from modules.VaultClient import VaultClient
import json
import datetime

class AccessManager(object):
    # TODO: add logger in this class
    def __init__(self, vault_client):
        self._vault_client = vault_client
        self._depositor_entity_id = self._vault_client.entity_id
    def grant_access(self, requester_entity_id, dataset_id, expiry_date=(datetime.date.today() + datetime.timedelta(days=7))):
        group_name = "_".join((self._depositor_entity_id, dataset_id, "share_group"))
        self._add_member_to_group(group_name, requester_entity_id, expiry_date)
    
    def _add_member_to_group(self, group_name, requester_entity_id, expiry_date):
        read_group_response = self._vault_client.read_group_by_name(group_name)
        member_entity_ids = read_group_response["data"]["member_entity_ids"]
        member_entity_ids.append(requester_entity_id)
        policies = read_group_response["data"]["policies"]
        metadata = read_group_response["data"]["metadata"]
        if metadata is None:
            metadata = {}
        metadata[requester_entity_id] = expiry_date.strftime("%Y-%m-%d")
        self._vault_client.create_or_update_group_by_name(group_name, policies, member_entity_ids, metadata)

    def revoke_access(self, requester_entity_id, dataset_id):
        group_name = "_".join((self._depositor_entity_id, dataset_id, "share_group"))
        self._remove_member_from_group(group_name, requester_entity_id)

    def _remove_member_from_group(self, group_name, requester_entity_id):
        read_group_response = self._vault_client.read_group_by_name(group_name)
        member_entity_ids = read_group_response["data"]["member_entity_ids"]
        member_entity_ids.remove(requester_entity_id)
        policies = read_group_response["data"]["policies"]
        metadata = read_group_response["data"]["metadata"]
        metadata.pop(requester_entity_id, None)
        self._vault_client.create_or_update_group_by_name(group_name, policies, member_entity_ids, metadata)

    def list_members(self):
        members = {}
        members["entity_id"] = self._depositor_entity_id
        members["data"] = []
        depositor_datasets = self._list_datasets()
        if depositor_datasets is None:
            return None
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

    def expire_shares(self):
        groups = self._vault_client.list_groups()
        for each_group in groups:
            read_group_response = self._vault_client.read_group_by_name(each_group)
            metadata = read_group_response["data"]["metadata"]
            if metadata is None:
                continue
            for key, value in metadata.items():
                expiry_date = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                if expiry_date <= datetime.date.today():
                    self._remove_member_from_group(each_group, key)
