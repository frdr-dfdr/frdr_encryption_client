#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
    expire_permission.py --vault <vault_addr> --tokenfile <root_tokenfile>

Options:
    --vault <vault_addr> using hashicorp vault for key generation and storage
    --tokenfile <root_tokenfile>
"""

import datetime
from docopt import docopt
from modules.VaultClient import VaultClient
from util import constants
from modules.AccessManager import AccessManager

__version__ = constants.VERSION

if __name__ == "__main__":
    arguments = docopt(__doc__, version=__version__)
    with open(arguments["--tokenfile"]) as f:
        vault_root_token = f.read()
    vault_client = VaultClient(vault_addr=arguments["--vault"], 
                               vault_token=vault_root_token)
    access_manager = AccessManager(vault_client)     
    access_manager.expire_shares()