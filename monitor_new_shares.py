#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
    monitor_new_shares.py --vault <vault_addr> --tokenfile <root_tokenfile>

Options:
    --vault <vault_addr> using hashicorp vault for key generation and storage
    --tokenfile <root_tokenfile>
"""

import subprocess
from email.message import EmailMessage
from docopt import docopt
from modules.VaultClient import VaultClient
from config import app_config
from modules.AccessManager import AccessManager
from util.util import Util
import os

__version__ = app_config.VERSION

if __name__ == "__main__":
    arguments = docopt(__doc__, version=__version__)
    Util.get_logger("cron-monitor-new-shares", 
                log_level="info",
                filepath=os.path.join(os.path.expanduser('~'), "logs", "new_shares_monitor.log"))
    with open(arguments["--tokenfile"]) as f:
        vault_root_token = f.read()
    vault_client = VaultClient(vault_addr=arguments["--vault"], 
                               vault_token=vault_root_token)  
    access_manager = AccessManager(vault_client)     
    access_manager.find_new_shares()
