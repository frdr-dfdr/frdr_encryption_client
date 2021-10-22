import hvac
import os
import logging 
import webbrowser
from urllib import parse
from util.util import Util
from util.config_loader import config
from hvac.exceptions import InvalidRequest

class VaultClient(object):
    def __init__(self):
        self._logger = logging.getLogger("fdrd-encryption-client.vault-client")
        self._vault_auth = None
        self._entity_id = None
        self.hvac_client = hvac.Client()
        self._vault_token = None

    def login(self, vault_addr, auth_method, username=None, password=None, oauth_type=None):
        self.hvac_client = hvac.Client(url=vault_addr)
        if auth_method == "userpass":
            if username is None or password is None:
                self._logger.error("Unable to load auth tokens from file, while username and password also not supplied. You need to obtain a login token with your username and password the first time you use the app.")
                return False
            try:
                response = self.hvac_client.auth.userpass.login(username, password)
                self._vault_token = response["auth"]["client_token"]
                return True
            except Exception:
                self._logger.error("Failed to auth with userpass method.")
                raise Exception
        # TODO: add other auth methods
        elif auth_method == "ldap":
            pass
        elif auth_method == "oidc":
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
                    redirect_uri='http://localhost:{}/{}/callback'.format(port, path),
                    path=path
                )
                auth_url = response['data']['auth_url']
                params = parse.parse_qs(auth_url.split('?')[1])
                auth_url_nonce = params['nonce'][0]
                auth_url_state = params['state'][0]

                webbrowser.open(auth_url)
                token = self._login_odic_get_token(port)

                auth_result = self.hvac_client.auth.oidc.oidc_callback(
                    code=token, path=path, nonce=auth_url_nonce, state=auth_url_state
                )
                self._vault_token = auth_result['auth']['client_token']
                self._entity_id = auth_result['auth']['entity_id']                
            except InvalidRequest as ir:
                self._logger.error("Failed to auth with {} account using oidc method. {}".format(oauth_type, ir))  
                #TODO: rewording
                raise TimeoutError("You login process has expired. Please try again")      
            except Exception as e:
                self._logger.error("Failed to auth with {} account using oidc method. {}".format(oauth_type, e))
                raise Exception(e)

        self.hvac_client.token = self._vault_token
        try:
            assert self.hvac_client.is_authenticated(), "Failed to authenticate with Vault."
        except AssertionError as error:
            self._logger.error(error)
            raise Exception(error)
        self._logger.info("Authenticated with Vault successfully.") 
    
    def logout(self):
        try:
            self.hvac_client.logout()
            self._logger.info("Logged out of Vault successfully.")
        except Exception:
            self._logger.error("Failed to log out of Vault.")
            raise Exception
   
    def enable_transit_engine(self):
        try:
            self.hvac_client.sys.enable_secrets_engine(backend_type="transit")
        except hvac.exceptions.InvalidRequest:
            self._logger.warning("Transit engine has been enabled.")

    def create_transit_engine_key_ring(self, name, mount_point=None, exportable=None, key_type=None):
        self.hvac_client.secrets.transit.create_key(name=name, 
                                                    mount_point=mount_point, 
                                                    exportable=exportable, 
                                                    key_type=key_type)

    def read_transit_key_rsa(self, name, mount_point=None):
        response = self.hvac_client.secrets.transit.read_key(name=name, mount_point=mount_point)
        public_key = response["data"]["keys"]["1"]["public_key"]
        return public_key
    
    def export_transit_key_rsa(self, name, mount_point=None):
        response = self.hvac_client.secrets.transit.export_key(name=name, key_type="encryption-key", mount_point=mount_point)
        private_key = response['data']['keys']['1']
        return private_key

    def generate_data_key(self, name, key_type="plaintext", mount_point=None):
        gen_key_response = self.hvac_client.secrets.transit.generate_data_key(name=name, key_type=key_type, mount_point=mount_point)
        key_plaintext = gen_key_response["data"]["plaintext"]
        return key_plaintext

    def decrypt_data_key(self, name, ciphertext):
        decrypt_data_response = self.hvac_client.secrets.transit.decrypt_data(name=name, ciphertext=ciphertext,)
        key_plaintext = decrypt_data_response["data"]["plaintext"]
        return key_plaintext

    def save_key_to_vault(self, path, key):
        self.hvac_client.secrets.kv.v2.create_or_update_secret(path=path, secret=dict(ciphertext=key))
    
    def retrive_key_from_vault(self, path):
        read_secret_response = self.hvac_client.secrets.kv.v2.read_secret_version(path=path)
        key_ciphertext = read_secret_response["data"]["data"]["ciphertext"]
        return key_ciphertext

    def read_entity_by_id(self, entity_id):
        try:
            response = self.hvac_client.secrets.identity.read_entity(entity_id=entity_id)
            if (len(response["data"]["aliases"]) > 0):
                return response["data"]["aliases"][0]["name"]
            else:
                return response["data"]["name"]
        except Exception as e:
            self._logger.error("error {}".format(e))
    
    def list_secrets(self, path):
        try:
            response = self.hvac_client.secrets.kv.v2.list_secrets(path)
            return response["data"]["keys"]
        except Exception as e:
            if str(e).startswith("None"):
                self._logger.info(str(e))
            else:
                self._logger.error("error {}".format(e))
    
    def list_groups(self):
        try:
            response = self.hvac_client.secrets.identity.list_groups_by_name()
            return response["data"]["keys"]
        except Exception as e:
            if str(e).startswith("None"):
                self._logger.info(str(e))
            else:
                self._logger.error("error {}".format(e))

    def read_secret_metadata(self, path):
        try:
            response = self.hvac_client.secrets.kv.v2.read_secret_metadata(path)
            return response["data"]["versions"]
        except Exception as e:
            if str(e).startswith("None"):
                self._logger.info(str(e))
            else:
                self._logger.error("error {}".format(e))
    
    def update_secret_metadata_delete_after(self, path, delete_after):
        self.hvac_client.secrets.kv.v2.update_metadata(path, delete_version_after=delete_after)

    def generate_certificate(self, name, common_name, mount_point=None):
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
    def _login_odic_get_token(self, port):
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
                self.wfile.write(str.encode('<div>Authentication successful, you can close the browser now.</div>'))

        server_address = ('', port)
        httpd = HttpServ(server_address, AuthHandler)
        httpd.timeout = config.VAULT_LOGIN_TIMEOUT
        httpd.handle_request()
        return httpd.token 

    @property
    def vault_auth(self):
        if self._vault_auth is None:
            self._vault_auth = self.lookup_token()
        return self._vault_auth

    @property
    def entity_id(self):
        return self._entity_id