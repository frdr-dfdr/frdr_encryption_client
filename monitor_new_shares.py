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
from util import constants
from modules.AccessManager import AccessManager

__version__ = constants.VERSION

def send_email(to_addrs, msg_subject, msg_body, from_addr=None):
    msg = EmailMessage()
    msg.set_content(msg_body)
    if from_addr is not None:
        msg['From'] = from_addr
    msg['To'] = to_addrs
    msg['Subject'] = msg_subject

    sendmail_location = "/usr/sbin/sendmail"
    subprocess.run([sendmail_location, "-t", "-oi"], input=msg.as_bytes())


if __name__ == "__main__":
    arguments = docopt(__doc__, version=__version__)
    with open(arguments["--tokenfile"]) as f:
        vault_root_token = f.read()
    vault_client = VaultClient(vault_addr=arguments["--vault"], 
                               vault_token=vault_root_token)  
    access_manager = AccessManager(vault_client)     
    access_manager.find_new_shares()
