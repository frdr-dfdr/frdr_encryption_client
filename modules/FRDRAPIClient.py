#
# Copyright (c) 2024 Digital Research Alliance of Canada
#
# This file is part of FRDR Encryption Application.
#
# FRDR Encryption Application is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the FRDR Encryption Application Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# FRDR Encryption Application is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRDR Encryption Application. If not, see <https://www.gnu.org/licenses/>.
#
from requests import request
from util.util import Util
from globus_sdk import GlobusAPIError, RefreshTokenAuthorizer, NativeAppAuthClient
from globus_sdk import BaseClient
import logging
from util.configLoader import config
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse


class DataPublicationClient(BaseClient):
    allowed_authorizer_types = [RefreshTokenAuthorizer]
    service_name = "datapublication"
    def __init__(self, base_url, **kwargs):
        self._logger = logging.getLogger(
            "frdr-encryption-application.DataPublicationClient")
        app_name = kwargs.pop(
            'app_name', config.GLOBUS_DATA_PUBLICATION_CLIENT_NAME)
        BaseClient.__init__(self, base_url=base_url,
                            app_name=app_name, **kwargs)
        self._headers = {'Content-Type': 'application/json'}

    def verify_requestitem_grant_access(self, dataset_uuid, requester_uuid):
        params = {
            "vault_dataset_id": dataset_uuid,
            "vault_requester_id": requester_uuid
        }
        return self.get('requestitem/grant-access/verify', query_params=params)

    def update_requestitem_grant_access(self, data):
        return self.put('requestitem/grant-access', data=data, headers=self._headers)

    def update_requestitem_decrypt(self, data):
        return self.put('requestitem/decrypt', data=data, headers=self._headers)
    
    def lookup_dataset_title(self, dataset_id):
        return self.get('dataset-title/{}'.format(dataset_id))

    def lookup_user_vault_id(self):
        return self.get('uservaultid')

    def update_user_vault_id(self, data):
        return self.put('uservaultid', data=data, headers=self._headers)


class FRDRAPIClient():

    def __init__(self, base_url):
        """Class init function 

        Args:
            base_url (string): FRDR API base url
        """
        self._logger = logging.getLogger(
            "frdr-encryption-application.FRDR-API-client")
        self._base_url = base_url
        self._pub_client = DataPublicationClient(base_url=self._base_url)

    def login(self, success_msg=None):
        """Log into FRDR for API usage.

        Args:
            success_msg (string, optional): The message shown in the browser once when the user logs in successfully. Defaults to None.

        Raises:
            Exception: If there is any error when logging into FRDR
        """
        if success_msg is None:
            success_msg = "Authentication to FRDR successful, you can close the browser now."
        try:
            tokens = self._interactive_login(success_msg)

            pub_tokens = tokens['publish.api.frdr.ca']

            pub_authorizer = RefreshTokenAuthorizer(
                refresh_token=pub_tokens['refresh_token'], 
                auth_client=self._load_auth_client(),
                access_token=pub_tokens['access_token'], 
                expires_at=pub_tokens['expires_at_seconds'])

            pub_client = DataPublicationClient(
                self._base_url, authorizer=pub_authorizer)
            self._pub_client = pub_client
        except Exception as e:
            self._logger.error(
                "Failed to auth for FRDR API usage. {}".format(e))
            raise Exception(e)

    
    def verify_requestitem_grant_access(self, dataset_uuid, requester_uuid):
        try:
            self._pub_client.verify_requestitem_grant_access(dataset_uuid, requester_uuid)
        except GlobusAPIError as e:
            self._logger.error("No pending requests for this dataset from this requester. {}".format(e.message))
            raise Exception("No pending requests for this dataset from this requester. {}".format(e.message))
        except Exception as e:
            self._logger.error("No pending requests for this dataset from this requester. {}".format(e))
            raise Exception("No pending requests for this dataset from this requester. {}".format(e))
    
    def update_requestitem_grant_access(self, data):
        """Update requestitem data on FRDR when depositors grant access
           to the key on FRDR Encryption Application.

        Args:
            data (dict): {"expires": The expiry data of the granted access, 
                          "vault_dataset_id": The id for the dataset on Vault,
                          "vault_requester_id": The id for the requester on Vault}

        Returns:
            [string]: REST API call response 
        """
        return self._pub_client.update_requestitem_grant_access(data)

    def update_requestitem_decrypt(self, data):
        """Update requestitem data on FRDR when depositors grant access
           to the key on FRDR Encryption Application.

        Args:
            data (dict): {"expires": The expiry data of the granted access, 
                          "vault_dataset_id": The id for the dataset on Vault,
                          "vault_requester_id": The id for the requester on Vault}

        Returns:
            [string]: REST API call response 
        """
        return self._pub_client.update_requestitem_decrypt(data)

    def get_dataset_title(self, dataset_id):
        """Look up the dataset title from FRDR using the dataset's vault id

        Args:
            dataset_id (string): The id for the dataset on Vault

        Raises:
            Exception: If there is an error when getting the information from FRDR

        Returns:
            string: The dataset title on FRDR
        """
        try:
            resp = self._pub_client.lookup_dataset_title(dataset_id)
            return resp['dataset_title']
        except Exception as e:
            self._logger.error("Error getting dataset title from FRDR {}".format(e))
            raise Exception(e)

    def get_user_vault_id_from_frdr(self):
        try:
            resp = self._pub_client.lookup_user_vault_id()
            return resp['user_vault_id']
        except Exception as e:
            self._logger.error("Error getting current user's vault id from FRDR {}".format(e))
            raise Exception(e)
        
    def send_user_vault_id_to_frdr(self, data):
        """Update requestitem data on FRDR when depositors grant access
           to the key on FRDR Encryption Application.

        Args:
            data (dict): {"expires": The expiry data of the granted access, 
                          "vault_dataset_id": The id for the dataset on Vault,
                          "vault_requester_id": The id for the requester on Vault}

        Returns:
            [string]: REST API call response 
        """
        return self._pub_client.update_user_vault_id(data)

    def _load_auth_client(self):
        return NativeAppAuthClient(
            config.GLOBUS_DATA_PUBLICATION_CLIENT_ID,
            app_name=config.GLOBUS_DATA_PUBLICATION_CLIENT_NAME)

    def _token_response_to_dict(self, token_response):
        resource_servers = ('publish.api.frdr.ca', )
        ret_toks = {}

        for res_server in resource_servers:
            try:
                token = token_response.by_resource_server[res_server]
                ret_toks[res_server] = token
            except:
                pass

        return ret_toks

    def _interactive_login(self, success_msg):
        native_client = self._load_auth_client()

        port = Util.find_free_port()
        native_client.oauth2_start_flow(
            requested_scopes=(
                'urn:globus:auth:scope:publish.api.frdr.org:all'),
            refresh_tokens=True,
            redirect_uri='http://localhost:{}'.format(port))
        auth_url = native_client.oauth2_get_authorize_url()
        webbrowser.open(auth_url)
        auth_code = self._login_get_token(port ,success_msg)

        if auth_code is None:
            raise TimeoutError(
                "You login process has expired. Please try again")

        tkns = native_client.oauth2_exchange_code_for_tokens(auth_code)
        return self._token_response_to_dict(tkns)

    def _login_get_token(self, port, success_msg):

        class HttpServ(HTTPServer):
            def __init__(self, *args, **kwargs):
                HTTPServer.__init__(self, *args, **kwargs)
                self.token = None

        class AuthHandler(BaseHTTPRequestHandler):
            token = ''

            def do_GET(self):
                params = parse.parse_qs(self.path.split('?')[1])
                self.server.token = params['code'][0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(str.encode(
                    "<div>{}</div>".format(success_msg)))

        server_address = ('', port)
        httpd = HttpServ(server_address, AuthHandler)
        httpd.timeout = config.FRDR_API_LOGIN_TIMEOUT
        httpd.handle_request()
        return httpd.token