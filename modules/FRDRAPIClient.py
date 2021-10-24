from util.util import Util
from globus_sdk import RefreshTokenAuthorizer, NativeAppAuthClient
from globus_sdk.base import BaseClient
import logging
from util.config_loader import config
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse


class DataPublicationClient(BaseClient):
    allowed_authorizer_types = [RefreshTokenAuthorizer]

    def __init__(self, base_url, **kwargs):
        self._logger = logging.getLogger(
            "fdrd-encryption-client.DataPublicationClient")
        app_name = kwargs.pop(
            'app_name', config.GLOBUS_DATA_PUBLICATION_CLIENT_NAME)
        BaseClient.__init__(self, "datapublication", base_url=base_url,
                            app_name=app_name, **kwargs)
        self._headers['Content-Type'] = 'application/json'

    def get_submission(self, submission_id, **params):
        return self.get('submissions/{}'.format(submission_id),
                        params=params)

    def update_requestitem(self, data):
        return self.put('requestitem', json_body=data)


class FRDRAPIClient(BaseClient):

    def __init__(self):
        self._logger = logging.getLogger(
            "fdrd-encryption-client.FRDR-API-client")
        self._pub_client = None

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

    def _interactive_login(self):
        native_client = self._load_auth_client()

        port = Util.find_free_port()
        native_client.oauth2_start_flow(
            requested_scopes=(
                'urn:globus:auth:scope:publish.api.frdr.org:all'),
            refresh_tokens=True,
            redirect_uri='http://localhost:{}'.format(port))
        auth_url = native_client.oauth2_get_authorize_url()
        webbrowser.open(auth_url)
        auth_code = self._login_get_token(port)

        if auth_code is None:
            raise TimeoutError(
                "You login process has expired. Please try again")

        tkns = native_client.oauth2_exchange_code_for_tokens(auth_code)
        return self._token_response_to_dict(tkns)

    def _login_get_token(self, port):

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
                    '<div>Authentication successful, you can close the browser now.</div>'))

        server_address = ('', port)
        httpd = HttpServ(server_address, AuthHandler)
        httpd.timeout = config.FRDR_API_LOGIN_TIMEOUT
        httpd.handle_request()
        return httpd.token

    def login(self, base_url):

        try:
            tokens = self._interactive_login()

            pub_tokens = tokens['publish.api.frdr.ca']

            pub_authorizer = RefreshTokenAuthorizer(
                pub_tokens['refresh_token'], self._load_auth_client(),
                pub_tokens['access_token'], pub_tokens['expires_at_seconds'])

            pub_client = DataPublicationClient(
                base_url, authorizer=pub_authorizer)
            self._pub_client = pub_client
        except Exception as e:
            self._logger.error(
                "Failed to auth for FRDR API usage. {}".format(e))
            raise Exception(e)

    def get_submission(self, submission_id):
        return self._pub_client.get_submission(submission_id)

    def update_requestitem(self, data):
        return self._pub_client.update_requestitem(data)
