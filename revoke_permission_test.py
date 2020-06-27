#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
    revoke_permission_test.py --hvac <vault_addr> --username <vault_username> --password <vault_password> --requester <requester_vault_entity_id> --name <dataset_name>

Options:
    --hvac <vault_addr> using hashicorp vault for key generation and storage
    -u <vault_username>, --username <vault_username>
    -p <vault_password>, --password <vault_password>
    -r <requester_vault_entity_id>, --requester <requester_vault_entity_id>
    -n <dataset_name>, --name <dataset_name>
"""
import os
from docopt import docopt
from appdirs import AppDirs
from modules.AccessGranter import AccessGranter
from modules.VaultClient import VaultClient
from util import constants
from util.util import Util
import click

__version__ = constants.VERSION
dirs = AppDirs(constants.APP_NAME, constants.APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)
tokenfile = os.path.join(dirs.user_data_dir, "vault_token")

if __name__ == "__main__":
    arguments = docopt(__doc__, version=__version__)
    vault_client = VaultClient(vault_addr=arguments["--hvac"], 
                               vault_username=arguments["--username"], 
                               vault_passowrd=arguments["--password"], 
                               tokenfile=tokenfile)
    access_granter = AccessGranter(vault_client)
    access_granter.revoke_access(arguments["--requester"], arguments["--name"])  