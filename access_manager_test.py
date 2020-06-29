#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
    access_manager_test.py --mode <mode> --vault <vault_addr> --username <vault_username> --password <vault_password> [--requester <requester_vault_entity_id>] [--name <dataset_name>]

Options:
    -m <mode>, --mode <mode> grant-access, revoke-access or review-shares
    --vault <vault_addr> using hashicorp vault for key generation and storage
    -u <vault_username>, --username <vault_username>
    -p <vault_password>, --password <vault_password>
    -r <requester_vault_entity_id>, --requester <requester_vault_entity_id>
    -n <dataset_name>, --name <dataset_name>
"""
import os
from docopt import docopt
from appdirs import AppDirs
from modules.AccessManager import AccessManager
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
    vault_client = VaultClient(vault_addr=arguments["--vault"], 
                               vault_username=arguments["--username"], 
                               vault_passowrd=arguments["--password"], 
                               tokenfile=tokenfile)
    access_granter = AccessManager(vault_client)
    if arguments["--mode"] == "review-shares":
        print (access_granter.list_members())
    else:
        requester_name = vault_client.read_entity_by_id(arguments["--requester"])
        if arguments["--mode"] == "grant-access":
            warning_string = "You are trying to grant requester {requester_name} access to dataset {dataset_id}"\
                            .format(requester_name=requester_name, dataset_id=arguments["--name"])
            print (Util.wrap_text(warning_string))
            if click.confirm("Do you want to continue?", default=False):
                access_granter.grant_access(arguments["--requester"], arguments["--name"])  
        elif arguments["--mode"] == "revoke-access":
            warning_string = "You are trying to revoke requester {requester_name} access to dataset {dataset_id}"\
                            .format(requester_name=requester_name, dataset_id=arguments["--name"])
            print (Util.wrap_text(warning_string))
            if click.confirm("Do you want to continue?", default=False):
                access_granter.revoke_access(arguments["--requester"], arguments["--name"])  
