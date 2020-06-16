from modules.VaultClient import VaultClient
import click
from util.util import Util

class AccessGranter(object):
    # TODO: add logger in this class
    def __init__(self, vault_client):
        self._vault_client = vault_client
        self._depositor_entity_id = self._vault_client.entity_id
    def grant_access(self, requester_entity_id, dataset_id):
        requester_name = self._vault_client.read_entity_by_id(requester_entity_id)
        warning_string = "You are tring to grant requester {requester_name} access to dataset {dataset_id}"\
                         .format(requester_name=requester_name, dataset_id=dataset_id)
        print (Util.wrap_text(warning_string))
        if click.confirm("Do you want to continue?", default=False):
            group_name = "_".join((self._depositor_entity_id, dataset_id, "share_group"))
            self._add_member_to_group(group_name, requester_entity_id)
    
    def _add_member_to_group(self, group_name, requester_entity_id):
        read_group_response = self._vault_client.read_group_by_name(group_name)
        member_entity_ids = read_group_response["data"]["member_entity_ids"]
        member_entity_ids.append(requester_entity_id)
        policies = read_group_response["data"]["policies"]
        self._vault_client.create_or_update_group_by_name(group_name, policies, member_entity_ids)
    