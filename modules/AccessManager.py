from modules.VaultClient import VaultClient
import json
import datetime
from collections import defaultdict
import datetime
from util.util import Util
from config import app_config
from dateutil import parser
import os
from pytz import timezone
import logging
import hvac

class AccessManager(object):
    def __init__(self, vault_client):
        self._vault_client = vault_client
        self._depositor_entity_id = self._vault_client.entity_id
        self._logger = logging.getLogger("fdrd-encryption-client.access-manager")

    def grant_access(self, requester_entity_id, dataset_id, expiry_date=None):
        if expiry_date is None:
            expiry_date = (datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
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
        access_updated_time = datetime.datetime.now(timezone(app_config.TIMEZONE)).isoformat()
        metadata[requester_entity_id] = expiry_date + "," + access_updated_time
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
            try:
                read_group_response = self._vault_client.read_group_by_name(group_name)
            except hvac.exceptions.InvalidPath:
                continue
            metadata = read_group_response["data"]["metadata"]
            if metadata is None:
                continue
            metadata_defaultdict = defaultdict(lambda: 'None', metadata)
            for each_member_id in self._list_members_per_group(group_name):
                each_member_name = self._vault_client.read_entity_by_id(each_member_id)
                each_member = {"entity_id": each_member_id, "entity_name": each_member_name, "expiry_date": metadata_defaultdict[each_member_id].split(",")[0]}
                each_dataset_members["members"].append(each_member)
            members["data"].append(each_dataset_members)
        return json.dumps(members)
    
    def _list_members_per_group(self, group_name):
        read_group_response = self._vault_client.read_group_by_name(group_name)
        member_entity_ids = read_group_response["data"]["member_entity_ids"]
        return member_entity_ids

    def _list_datasets(self):        
        return self._vault_client.list_secrets(self._depositor_entity_id)

    def check_access(self):
        self._logger = logging.getLogger("cron-monitor-expired-shares.access-manager")
        groups = self._vault_client.list_groups()
        if groups is None:
            return None
        for each_group in groups:
            read_group_response = self._vault_client.read_group_by_name(each_group)
            dataset_id = read_group_response["data"]["name"].split("_")[1]
            metadata = read_group_response["data"]["metadata"]
            if metadata is None:
                continue
            for key, value in metadata.items():
                expiry_date = datetime.datetime.strptime(value.split(",")[0], "%Y-%m-%d").date()
                self._logger.info("Expire date for user {} of dataset {} is {}".format(key, each_group.split("_")[1], expiry_date))
                self._logger.info("Today is {}".format(datetime.date.today()))
                # Expire shares
                if expiry_date < datetime.date.today():
                    self._remove_member_from_group(each_group, key)
                    self._logger.info("User {}'s access to dataset {} has expired.".format(key, each_group.split("_")[1]))
                # Send notice three days before access expires
                if expiry_date == (datetime.date.today() + datetime.timedelta(days=3)):
                    self._send_notice(key, dataset_id, expiry_date)
                    self._logger.info("User {}'s access to dataset {} will expire in three days. Notice email sent to user."\
                        .format(key, each_group.split("_")[1]))

    def _send_notice(self, requester_entity_id, dataset_id, expiry_date):
        requester_email = self._vault_client.read_entity_by_id(requester_entity_id)
        subject = "Vault - Access to sensitive data's key expires soon"
        body_html = """\
            <html>
                <body>
                    <p>
                        Attention: 
                    </p>
                    <p>
                        Please note that your access to the key of an encrypted dataset with \
                        the metatdata frdr.vault.dataset_uuid {dataset_id} will expire on {expiry_date}. \
                        Please ensure you have downloaded the dataset from FRDR and decrypted it prior \
                        to {expiry_date}. After {expiry_date} you will no longer be able to \
                        access the key.
                    </p>
                    <p>
                        If you encounter any problems or have other questions, please contact us at \
                        support@frdr-dfdr.ca. Best of luck with the data!
                    </p>
                    <br/><br/>
                    FRDR Support
                    support@frdr-dfdr.ca
                </body>
            </html>
            """.format(dataset_id=dataset_id, expiry_date=expiry_date)
        Util.send_email(requester_email, subject, body_html)
    
    def find_new_shares(self):
        self._logger = logging.getLogger("cron-monitor-new-shares.access-manager")
        groups = self._vault_client.list_groups()
        if groups is None:
            return None
        for each_group in groups:
            read_group_response = self._vault_client.read_group_by_name(each_group)
            metadata = read_group_response["data"]["metadata"]
            group_last_update_time = parser.isoparse(read_group_response["data"]["last_update_time"])
            now = datetime.datetime.now(timezone(app_config.TIMEZONE)) 
            if (group_last_update_time <= (now - datetime.timedelta(hours=6))):
                continue  

            # no requesters to this dataset
            if metadata is None:
                continue
            depositor_user_id = read_group_response["data"]["name"].split("_")[0]
            dataset_id = read_group_response["data"]["name"].split("_")[1]
            for key, value in metadata.items():
                if len(value.split(",")) > 1:
                    expiry_date = datetime.datetime.strptime(value.split(",")[0], "%Y-%m-%d").date()
                    access_updated_time = parser.parse(value.split(",")[1])
                    if access_updated_time <= now and access_updated_time >= (now - datetime.timedelta(minutes=1)):
                        vault_api_url = "http://206-12-90-40.cloud.computecanada.ca/secret/data/{depositor_user_id}/{dataset_id}"\
                                        .format(depositor_user_id=depositor_user_id, dataset_id=dataset_id)
                        app_download_url = "https://github.com/jza201/frdr-secure-data/releases/tag/0.1.0"
                        requester_email = self._vault_client.read_entity_by_id(key)
                        subject = "Vault - Access granted to the request copy of item"
                        body_html = """\
                            <html>
                                <body>
                                    <p>
                                        Attention: 
                                    </p>
                                    <p>
                                        Congratulations! You have been granted access to an encrypted dataset with \
                                        the metatdata frdr.vault.dataset_uuid {dataset_id} on FRDR. You will be \
                                        receiving a second email that contains similar text to this one which has \
                                        been generated from a separate platform. This is not a duplicate of that \
                                        message; they are sent separately in order to maintain zero-knowledge \
                                        encryption between the dataset and the encryption key. You will use \
                                        information from both email messages in order to access the dataset.
                                    </p>
                                    <p>
                                        Please refer first to the other email message from FRDR in order to download the \
                                        dataset from FRDR. Once the encrypted dataset has been downloaded, you will need \
                                        to run our <b>FRDR Encryption App</b> to decrypt the dataset. The app can be \
                                        downloaded {app_download_url}. Navigate to the <b>Decrypt</b> menu and input \
                                        your FRDR credentials, and provide the path to the encrypted dataset that you \
                                        already downloaded, and a Vault API URL (provided below) that has been generated \
                                        for you to access the decryption key for this dataset. Please refer to this guide \
                                        for assistance: [LINK]
                                    </p>
                                    <p>
                                        Please note that your access to this dataset will expire on {expiry_date}. \
                                        Please ensure you have downloaded the dataset from FRDR and decrypted it prior \
                                        to {expiry_date}. After {expiry_date} you will no longer be able to \
                                        access the dataset.
                                    </p>
                                    <p> Your Vault API URL is: {vault_api_url} </p>
                                    <p>
                                        We strongly recommend only decrypting this data on a trusted computer which is itself \
                                        encrypted (e.g. using Windows' BitLocker or Apple's FileVault functionality) and \
                                        accessed only by you. Please refer to your institutional requirements for accessing \
                                        sensitive datasets here: [LINK].Please ensure all protocols are followed to prevent data breach.
                                    </p>
                                    <p>
                                        If you encounter any problems or have other questions, please contact us at \
                                        support@frdr-dfdr.ca. Best of luck with the data!
                                    </p>
                                    <br/><br/>
                                    FRDR Support
                                    support@frdr-dfdr.ca
                                </body>
                            </html>
                            """.format(dataset_id=dataset_id, expiry_date=expiry_date, app_download_url=app_download_url, vault_api_url=vault_api_url)
                        Util.send_email(requester_email, subject, body_html)
                        self._logger.info("New access granted to {} at {}".format(requester_email, access_updated_time))
