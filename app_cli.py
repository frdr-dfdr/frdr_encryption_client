#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
    app_cli.py -e -i <input_path> [-o <output_path>] [--vault <vault_addr>] [--username <vault_username>] [--password <vault_password>] [<oauth_type>] [--loglevel=<loglevel>] 
    app_cli.py -d -i <input_path> [-o <output_path>] (--key <key_path> | --vault <vault_addr> (--username <vault_username> --password <vault_password> | <oauth_type>) --url <API_path>) [--loglevel=<loglevel>] 
    app_cli.py --vault <vault_addr> --vault_pki <pki_vault_addr> --oauth <oauth_type> -i <input_path> [-o <output_path>]

Options:
    -e --encrypt           encrypt
    -d --decrypt           decrypt
    --oauth <oauth_type>
    -i <input_path>, --input <input_path>
    -o <output_path>, --output <output_path> 
    -k <key_path>, --key <key_path>
    --vault <vault_addr> using hashicorp vault for key generation and storage
    --vault_pki <pki_vault_addr> using hashicorp vault for key generation and storage
    -u <vault_username>, --username <vault_username>
    -p <vault_password>, --password <vault_password>
    --token <vault_token> 
    --logout_vault  Remove old vault tokens
    --url <API_path>  API Path to fetch secret on vault
    -l --loglevel The logging level(debug, error, warning or info) [default: info]
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

        if (arguments["--input"] is not None) and (not Util.check_dir_exists(arguments["--input"])):
            logger.error("The input directory does not exist.")
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
                                   auth_method="oidc",
                                   oauth_type=arguments["--oauth"])
            
            operation = input("Please type in the operation you would like to do, encrypt, decrypt, or grant access: ")    
            if operation == "encrypt":
                dataset_uuid = str(uuid.uuid4())  
                dataset_key_manager = DatasetKeyManager(vault_client)
                person_key_manager = PersonKeyManager(vault_client)
                # TODO: add argument for input dir and output dir
                encryptor = EncryptionClient(dataset_key_manager, person_key_manager, arguments["--input"], arguments["--output"])
                encryptor.encrypt(dataset_uuid)
            elif operation == "decrypt":
                #TODO: rewording
                url = input("Please type in the url: ")
                dataset_key_manager = DatasetKeyManager(vault_client)
                person_key_manager = PersonKeyManager(vault_client)
                # TODO: add argument for input dir and output dir
                encryptor = EncryptionClient(dataset_key_manager, person_key_manager, arguments["--input"], arguments["--output"])
                encryptor.decrypt(url)
            elif operation == "grant-access":
                #TODO: rewording
                requester_uuid = input("Please type in the requester vault entity id: ")
                dataset_uuid = input("Please type in the dataset uuid on Vault that you want to grant access: ")
                expire_date = input("Please type in the expire date in format YYYY-mm-dd")
                if click.confirm("Do you want to continue?", default=False):
                    dataset_key_manager = DatasetKeyManager(vault_client)
                    person_key_manager = PersonKeyManager(vault_client)
                    encryptor = EncryptionClient(dataset_key_manager, person_key_manager)
                    encryptor.grant_access(requester_uuid, dataset_uuid, expire_date)  
            elif operation == "generate-access-request":
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