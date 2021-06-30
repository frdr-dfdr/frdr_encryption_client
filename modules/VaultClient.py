import hvac
import os
import logging 
import webbrowser
from urllib import parse

class VaultClient(object):
    def __init__(self):
        self._logger = logging.getLogger("frdr-crypto.vault-client")
        self._vault_auth = None
        self._entity_id = None
        self.hvac_client = hvac.Client()
        # TODO: decide whether need this
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
                if self._tokenfile:
                    self.write_token_to_file()
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
                response = self.hvac_client.auth.jwt.oidc_authorization_url_request(
                    role='',
                    redirect_uri='http://localhost:8250/{}/callback'.format(path),
                    path=path
                )
                auth_url = response['data']['auth_url']
                params = parse.parse_qs(auth_url.split('?')[1])
                auth_url_nonce = params['nonce'][0]
                auth_url_state = params['state'][0]

                webbrowser.open(auth_url)
                token = self._login_odic_get_token()

                auth_result = self.hvac_client.auth.oidc.oidc_callback(
                    code=token, path=path, nonce=auth_url_nonce, state=auth_url_state
                )
                self._vault_token = auth_result['auth']['client_token']
                self._logger.info("Authenticated with Vault successfully.")
                return True                                    
            except Exception as e:
                self._logger.error("Failed to auth with {} account using oidc method. {}".format(oauth_type, e))
                raise Exception

        try:
            assert self.hvac_client.is_authenticated(), "Failed to authenticate with Vault."
        except AssertionError as error:
            self._logger.error(error)
            raise Exception(error)
        
    def logout(self):
        try:
            self.hvac_client.logout()
            self._logger.info("Logged out of Vault successfully.")
        except Exception:
            self._logger.error("Failed to log out of Vault.")
            raise Exception
        
    def load_token_from_file(self):
        if os.path.exists(self._tokenfile):
            with open(self._tokenfile) as f:
                self._vault_token = f.read()
            if self._vault_token is not None:
                return True
        return None
    
    def write_token_to_file(self):
        #TODO: decide whether to save auth to file or not
        pass
        # with open(self._tokenfile, "w") as f:
        #     f.write(self._vault_token)  
   
    def enable_transit_engine(self):
        try:
            self.hvac_client.sys.enable_secrets_engine(backend_type="transit")
        except hvac.exceptions.InvalidRequest:
            self._logger.warning("Transit engine has been enabled.")

    def create_transit_engine_key_ring(self, name):
        self.hvac_client.secrets.transit.create_key(name=name)

    def generate_data_key(self, name, key_type="plaintext"):
        gen_key_response = self.hvac_client.secrets.transit.generate_data_key(name=name, key_type=key_type,)
        key_plaintext = gen_key_response["data"]["plaintext"]
        key_ciphertext = gen_key_response["data"]["ciphertext"]
        return (key_plaintext, key_ciphertext)

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

    def create_policy(self, policy_name, policy_string):
        return self.hvac_client.sys.create_or_update_policy(name=policy_name, policy=policy_string,)

    def read_policy(self, policy_name):
        return self.hvac_client.sys.read_policy(policy_name)

    def create_or_update_group_by_name(self, group_name, policy_name=None, member_entity_ids=None, metadata=None):
        return self.hvac_client.secrets.identity.create_or_update_group_by_name(
            name=group_name,
            group_type="internal",
            policies=policy_name,
            member_entity_ids=member_entity_ids,
            metadata=metadata,
        )
    def read_group_by_name(self, group_name):
        return self.hvac_client.secrets.identity.read_group_by_name(group_name)

    def read_entity_by_id(self, entity_id):
        try:
            response = self.hvac_client.secrets.identity.read_entity(entity_id=entity_id)
            if (len(response["data"]["aliases"]) > 0):
                return response["data"]["aliases"][0]["name"]
            else:
                return response["data"]["name"]
        except Exception as e:
            self._logger.error("error {}".format(e))
    
    def list_secrets(self, entity_id):
        try:
            response = self.hvac_client.secrets.kv.v2.list_secrets(entity_id)
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

    def lookup_token(self):
        try: 
            response = self.hvac_client.lookup_token()
            return response["data"]
        except Exception as e:
            self._logger.error("error {}".format(e))



    # handles the callback
    def _login_odic_get_token(self):
        from http.server import BaseHTTPRequestHandler, HTTPServer

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
                self.wfile.write(str.encode('<div>Authentication successful, you can close the browser now.</div>'))

        server_address = ('', 8250)
        httpd = HttpServ(server_address, AuthHandler)
        httpd.handle_request()
        return httpd.token 

    @property
    def vault_auth(self):
        if self._vault_auth is None:
            self._vault_auth = self.lookup_token()
        return self._vault_auth

    # @property
    # def vault_token(self):
    #     # self._vault_token is an empty string, not None
    #     if not self._vault_token:
    #         if self.load_token_from_file():
    #             self._logger.info("Token loaded from file")
    #         else:
    #             self.login(self._auth_method, self._username, self._password, self._oauth_type)
    #     return self._vault_token

    @property
    def entity_id(self):
        if self._entity_id is None:
            try:
                self._entity_id = self.vault_auth["entity_id"]
            except:
                self._entity_id = None
        return self._entity_id