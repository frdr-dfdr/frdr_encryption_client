#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
  app_cli.py encrypt --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>) --input=<ip> [--output=<op>] [--loglevel=<l>]
  app_cli.py decrypt --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>) --input=<ip> --url=<key_addr> [--output=<op>] [--loglevel=<l>]
  app_cli.py grant_access --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>) --dataset=<id> --requester=<id> --expire=<date> [--loglevel=<l>]
  app_cli.py generate_access_request --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>)
  app_cli.py -h | --help

Options:
  -h --help     Show this screen.
  --username=<un>  username.
  --password=<pd>  password.
  --vault=<vault_addr>
  --input=<ip>
  --output=<op>
  --url=<key_addr>
  --dataset=<id>
  --requester=<id>
  --expire=<date>  the permission expiry date in format YYYY-mm-dd
  --loglevel=<l>  loglevel [default: info].
"""
from modules.PersonKeyManager import PersonKeyManager
from modules.EncryptionClient import EncryptionClient
from docopt import docopt
import sys
import os
from util.util import Util
from config import app_config
from modules.VaultClient import VaultClient
from modules.DatasetKeyManager import DatasetKeyManager
from appdirs import AppDirs
import uuid
import click

__version__ = app_config.VERSION
dirs = AppDirs(app_config.APP_NAME, app_config.APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)

def main():
    try:
        arguments = docopt(__doc__, version=__version__)
        logger = Util.get_logger("fdrd-encryption-client", 
                                log_level=arguments["--loglevel"],
                                filepath=os.path.join(dirs.user_data_dir, "fdrd-encryption-client_log.txt"))
        if sys.version_info[0] < 3:
            raise Exception("Python 3 is required to run the local client.")

        vault_client = VaultClient()
        print (arguments)

        if (arguments["encrypt"]) and (not Util.check_dir_exists(arguments["--input"])):
            logger.error("The input directory does not exist.")
            # TODO: raise Exception or return to exit
            # raise Exception
            return 

        if (arguments["decrypt"]) and (not Util.check_dir_exists(arguments["--input"])):
            logger.error("The input zip file does not exist.")
            # TODO: raise Exception or return to exit
            return 
        
        if (arguments["--output"] is not None) and (not Util.check_dir_exists(arguments["--output"])):
            logger.error("The output directory does not exist.")
            # TODO: raise Exception or return to exit
            return 

        if arguments["--vault"]:
            if arguments["--username"]:
                vault_client.login(vault_addr=arguments["--vault"],
                                   auth_method="userpass",
                                   username=arguments["--username"], 
                                   password=arguments["--password"])
            elif arguments["--oauth"]:
                vault_client.login(vault_addr=arguments["--vault"],
                                   auth_method="oidc")
            
            if arguments["encrypt"]:
                print (arguments["--input"])
                if not Util.check_dir_exists(arguments["--input"]):
                    logger.error("The input directory does not exist.")
                    # TODO: raise Exception or return to exit
                    return 
                dataset_uuid = str(uuid.uuid4())  
                dataset_key_manager = DatasetKeyManager(vault_client)
                person_key_manager = PersonKeyManager(vault_client)
                # TODO: add argument for input dir and output dir
                encryptor = EncryptionClient(dataset_key_manager, person_key_manager, arguments["--input"], arguments["--output"])
                encryptor.encrypt(dataset_uuid)
            elif arguments["decrypt"]:
                url = arguments["--url"]
                dataset_key_manager = DatasetKeyManager(vault_client)
                person_key_manager = PersonKeyManager(vault_client)
                # TODO: add argument for input dir and output dir
                encryptor = EncryptionClient(dataset_key_manager, person_key_manager, arguments["--input"], arguments["--output"])
                encryptor.decrypt(url)
            elif arguments["grant_access"]:
                requester_uuid = arguments["--requester"]
                dataset_uuid = arguments["--dataset"]
                expire_date = arguments["--expire"]
                if click.confirm("Do you want to continue?", default=False):
                    dataset_key_manager = DatasetKeyManager(vault_client)
                    person_key_manager = PersonKeyManager(vault_client)
                    encryptor = EncryptionClient(dataset_key_manager, person_key_manager)
                    encryptor.grant_access(requester_uuid, dataset_uuid, expire_date)  
            elif arguments["generate_access_request"]:
                entity_id = vault_client.entity_id
                person_key_manager = PersonKeyManager(vault_client)
                # make sure there is a public key saved on Vault for the requester
                person_key_manager.create_or_retrieve_public_key()
                print ("Please copy the following id to the Requester ID Field on the Access Request Page on FRDR.")
                print (Util.wrap_text(entity_id))
                           
    except Exception as e:
        logger.error("Exception caught, exiting. {}".format(e), exc_info=True)

if __name__ == "__main__":
    main()