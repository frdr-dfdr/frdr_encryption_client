#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
    expire_permission.py --vault <vault_addr> --tokenfile <root_tokenfile>

Options:
    --vault <vault_addr> using hashicorp vault for key generation and storage
    --tokenfile <root_tokenfile>
"""

from docopt import docopt
from modules.VaultClient import VaultClient
from config import app_config
from util.util import Util
from modules.AccessManager import AccessManager
import os

__version__ = app_config.VERSION

if __name__ == "__main__":
    arguments = docopt(__doc__, version=__version__)
    Util.get_logger("cron-monitor-expired-shares", 
            log_level="info",
            filepath=os.path.join(os.path.expanduser('~'), "logs", "permission_monitor.log"))
    with open(arguments["--tokenfile"]) as f:
        vault_root_token = f.read()
    vault_client = VaultClient(vault_addr=arguments["--vault"], 
                               vault_token=vault_root_token)
    access_manager = AccessManager(vault_client)     
    access_manager.check_access()