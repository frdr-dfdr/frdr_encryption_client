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

import hvac
import logging
import webbrowser
from urllib import parse
from util.util import Util
from util.configLoader import config
from hvac.exceptions import InvalidRequest


class VaultClient(object):
    def __init__(self, token=None, url=None, entity_id=None):
        """Init function of VaultClient. 
           In normal case, no parameter is required for initilization. 
           If token, url and entity_id are given, it means the VaultClient
           has already been authenticated for usage. This is added to support 
           calling the encrypt function in EncryptionClientGui in a separate 
           process.

        Args:
            token (string, optional): Authentication token to include in requests sent to Vault. Defaults to None.
            url (string, optional): Base URL for the Vault instance being addressed. Defaults to None.
            entity_id (string, optional): The authenticated user's id on Vault. Defaults to None.
        """
        self._logger = logging.getLogger("frdr-encryption-client.vault-client")
        self.hvac_client = hvac.Client(token=token, url=url)
        self._entity_id = entity_id

    def login(self, vault_addr, auth_method, username=None, password=None, oauth_type=None, success_msg=None):
        
        """Log into the key server (HashiCorp Vault) with different auth methods. 
           It currently supports OIDC auth method which is configured to allow 
           users to use their Globus Credentials, and userpass auth method. 

        Args:
            vault_addr (string): The HashiCorp Vault address
            auth_method (string): "userpass" or "oidc"
            username (string, optional): Username is using userpass as the auth method. Defaults to None.
            password (string, optional): Password is using userpass as the auth method. Defaults to None.
            oauth_type (string, optional): The oidc provider if multiple oidc providers are needed. Defaults to None.
            success_msg (string, optional): The message shown in the browser once when the user logs in successfully. Defaults to None.

        Raises:
            Exception: If there is any error when logging in with userpass auth method
            TimeoutError: If user has not finished the login process in time with oidc auth method
            Exception: If there is any error when logging in with oidc auth method
            AssertionError: If the Vault client is not authenticated after login process
        """
        self.hvac_client = hvac.Client(url=vault_addr)
        if auth_method == "userpass":
            if username is None or password is None:
                self._logger.error(
                    "Unable to load auth tokens from file, while username and password also not supplied. \
                    You need to obtain a login token with your username and password the first time you use the app.")
            try:
                response = self.hvac_client.auth.userpass.login(
                    username, password)
                vault_token = response["auth"]["client_token"]
            except Exception:
                self._logger.error("Failed to auth with userpass method.")
                raise Exception
        # TODO: add other auth methods
        elif auth_method == "ldap":
            pass
        elif auth_method == "oidc":
            if success_msg is None:
                success_msg = "Authentication to HashiCorp Vault successful, you can close the browser now."
            try:
                if oauth_type is None:
                    path = "oidc"
                    # self._logger.error("Account type must be provided for oidc login mehtod")
                    # return False
                else:
                    path = "oidc/" + oauth_type
                port = Util.find_free_port()
                response = self.hvac_client.auth.jwt.oidc_authorization_url_request(
                    role='',
                    redirect_uri='http://localhost:{}/{}/callback'.format(
                        port, path),
                    path=path
                )
                auth_url = response['data']['auth_url']
                params = parse.parse_qs(auth_url.split('?')[1])
                auth_url_nonce = params['nonce'][0]
                auth_url_state = params['state'][0]

                webbrowser.open(auth_url)
                token = self._login_odic_get_token(port, success_msg)

                auth_result = self.hvac_client.auth.oidc.oidc_callback(
                    code=token, path=path, nonce=auth_url_nonce, state=auth_url_state
                )
                vault_token = auth_result['auth']['client_token']
                self._entity_id = auth_result['auth']['entity_id']
            except InvalidRequest as ir:
                self._logger.error(
                    "Failed to auth with {} account using oidc method. {}".format(oauth_type, ir))
                #TODO: rewording
                raise TimeoutError(
                    "Your login process has expired. Please try again")
            except Exception as e:
                self._logger.error(
                    "Failed to auth with {} account using oidc method. {}".format(oauth_type, e))
                raise Exception(e)

        self.hvac_client.token = vault_token
        try:
            assert self.hvac_client.is_authenticated(), "Failed to authenticate with Vault."
        except AssertionError as error:
            self._logger.error(error)
            raise AssertionError(error)
        self._logger.info("Authenticated with Vault successfully.")

    def logout(self):
        """Log out of the key server (HashiCorp Vault).

        Raises:
            Exception: If there is any error when logging out
        """
        try:
            self.hvac_client.logout()
            self._logger.info("Logged out of Vault successfully.")
        except Exception:
            self._logger.error("Failed to log out of Vault.")
            raise Exception

    def enable_transit_engine(self):
        """Enable the transit secrets engine.
        """
        try:
            self.hvac_client.sys.enable_secrets_engine(backend_type="transit")
        except hvac.exceptions.InvalidRequest:
            self._logger.warning("Transit engine has been enabled.")

    def create_transit_engine_key_ring(self, name, mount_point=None, exportable=None, key_type=None):
        """Create a new named encryption key ring on Vault for dataset key generation.

        Args:
            name (string): The name of the encryption key ring to create.
            mount_point (string, optional): The path the method/backend was mounted on. Defaults to None.
            exportable (boolean, optional): Enables keys to be exportable. This allows for all the valid keys in the key ring to be exported. Defaults to None.
            key_type (string, optional): The type of key to create. Defaults to None.
        """
        self.hvac_client.secrets.transit.create_key(name=name,
                                                    mount_point=mount_point,
                                                    exportable=exportable,
                                                    key_type=key_type)

    def generate_data_key(self, name, key_type="plaintext", mount_point=None):
        """Generate a new key and the value encrypted with the named key ring, which
           is the dataset key to use for dataset encryption.

        Args:
            name (string): The name of the encryption key ring to use to encrypt the datakey.
            key_type (string, optional): The type of key to generate. If plaintext, the plaintext 
                                      key will be returned along with the ciphertext. If wrapped, 
                                      only the ciphertext value will be returned. Defaults to "plaintext".
            mount_point (string, optional): The path the method/backend was mounted on.. Defaults to None.

        Returns:
            string: The data key 
        """
        gen_key_response = self.hvac_client.secrets.transit.generate_data_key(
            name=name, key_type=key_type, mount_point=mount_point)
        key_plaintext = gen_key_response["data"]["plaintext"]
        return key_plaintext

    def save_key_to_vault(self, path, key):
        """Save the key at the specified location.

        Args:
            path (string): The path the key is saved at.
            key (string): The key to save on HashiCorp Vault.
        """
        self.hvac_client.secrets.kv.v2.create_or_update_secret(
            path=path, secret=dict(ciphertext=key))

    def delete_key_on_vault(self, path):
        self.hvac_client.secrets.kv.v2.delete_metadata_and_all_versions(path)

    def retrive_key_from_vault(self, path):
        """Retrieve the key at the specified location.

        Args:
            path (string): The path the key is saved at.

        Returns:
            string: The key saved on HashiCorp Vault.
        """
        try:
            read_secret_response = self.hvac_client.secrets.kv.v2.read_secret_version(path=path)
            key_ciphertext = read_secret_response["data"]["data"]["ciphertext"]
            return key_ciphertext
        except Exception as e:
            self._logger.error("error {}".format(e))
            return None

    def read_entity_by_id(self, entity_id):
        """Query an entity's name by its identifier.

        Args:
            entity_id (string): Identifier of the entity.

        Returns:
            string: Entity's name saved on HashiCorp Vault.
        
        Raises:
            Exception: If there is any error when reading entity of user on HashiCorp Vault.
        """
        try:
            response = self.hvac_client.secrets.identity.read_entity(
                entity_id=entity_id)
            if (len(response["data"]["aliases"]) > 0):
                return response["data"]["aliases"][0]["name"]
            else:
                return response["data"]["name"]
        except Exception as e:
            self._logger.error("Error reading entity of user from Vault {}".format(e))
            raise Exception(e)

    def list_secrets(self, path):
        """Return a list of key names at the specified location.

        Args:
            path (string): The path of the secrets to list.

        Returns:
            [list]: The list of key names at the specified location.
        """
        try:
            response = self.hvac_client.secrets.kv.v2.list_secrets(path)
            return response["data"]["keys"]
        except Exception as e:
            if str(e).startswith("None"):
                self._logger.info(str(e))
            else:
                self._logger.error("error {}".format(e))

    def update_secret_metadata_delete_after(self, path, delete_after):
        """Update the 'delete_after' metadata of a secret at the specified location.

        Args:
            path (string): The path of the secret to update.
            delete_after (string): The length of time before a version is deleted. 
        """
        self.hvac_client.secrets.kv.v2.update_metadata(
            path, delete_version_after=delete_after)

    def generate_certificate(self, name, common_name, mount_point=None):
        """Generate a new set of credentials (certificate and private key)
           based on the role named in the endpoint.

        Args:
            name (string): The name of the role to create the certificate against. 
            common_name (string): The requested CN for the certificate.
            mount_point (string, optional):  The path the method/backend was mounted on. Defaults to None.

        Returns:
            tuple(string, string): certificate and private key
        """
        try:
            response = self.hvac_client.secrets.pki.generate_certificate(
                name=name,
                common_name=common_name,
                mount_point=mount_point
            )
            certificate = response['data']['certificate']
            private_key = response['data']['private_key']
            return (certificate, private_key)
        except Exception as e:
            if str(e).startswith("None"):
                self._logger.info(str(e))
            else:
                self._logger.error("error {}".format(e))

    # handles the callback
    def _login_odic_get_token(self, port, success_msg):
        from http.server import BaseHTTPRequestHandler, HTTPServer

        class HttpServ(HTTPServer):
            def __init__(self, *args, **kwargs):
                HTTPServer.__init__(self, *args, **kwargs)
                self.token = None
                self.allow_reuse_address = True

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
        httpd.timeout = config.VAULT_LOGIN_TIMEOUT
        httpd.handle_request()
        return httpd.token
    
    def get_hvac_client(self):
        return self.hvac_client

    @property
    def entity_id(self):
        return self._entity_id

    @property
    def token(self):
        return self.hvac_client.token

    @property
    def url(self):
        return self.hvac_client.url
