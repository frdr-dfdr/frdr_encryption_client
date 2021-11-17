#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
  app_cli.py encrypt --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>) --input=<ip> [--output=<op>] [--loglevel=<l>]
  app_cli.py decrypt --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>) --input=<ip> --url=<key_addr> [--output=<op>] [--loglevel=<l>]
  app_cli.py grant_access --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>) --dataset=<id> --requester=<id> --expire=<date> [--frdr_api_url=<url>] [--loglevel=<l>]
  app_cli.py show_vault_id --vault=<vault_addr> (--oauth | --username=<un> --password=<pd>)
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
  --frdr_api_url=<url>
  --loglevel=<l>  loglevel [default: info].
"""

from modules.FRDRAPIClient import FRDRAPIClient
from modules.PersonKeyManager import PersonKeyManager
from modules.EncryptionClient import EncryptionClient
from docopt import docopt
import sys
import os
from util.util import Util
from util.config_loader import config
from modules.VaultClient import VaultClient
from modules.DatasetKeyManager import DatasetKeyManager
from appdirs import AppDirs
import uuid
import click

__version__ = config.VERSION
dirs = AppDirs(config.APP_NAME, config.APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)


def main():
    try:
        arguments = docopt(__doc__, version=__version__)
        logger = Util.get_logger("frdr-encryption-client",
                                 log_level=arguments["--loglevel"],
                                 filepath=os.path.join(dirs.user_data_dir, config.APP_LOG_FILENAME))
        if sys.version_info[0] < 3:
            raise Exception("Python 3 is required to run the local client.")

        vault_client = VaultClient()

        if (arguments["encrypt"]) and (not Util.check_dir_exists(arguments["--input"])):
            raise ValueError("The input directory does not exist.")

        if (arguments["decrypt"]) and (not Util.check_dir_exists(arguments["--input"])):
            raise ValueError("The input zip file does not exist.")

        if (arguments["--output"] is not None) and (not Util.check_dir_exists(arguments["--output"])):
            raise ValueError("The output directory does not exist.")

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
                dataset_uuid = str(uuid.uuid4())
                dataset_key_manager = DatasetKeyManager(vault_client)
                person_key_manager = PersonKeyManager(vault_client)
                encryptor = EncryptionClient(
                    dataset_key_manager, person_key_manager, arguments["--input"], arguments["--output"])
                encryptor.encrypt(dataset_uuid)

            elif arguments["decrypt"]:
                url = arguments["--url"]
                dataset_key_manager = DatasetKeyManager(vault_client)
                person_key_manager = PersonKeyManager(vault_client)
                encryptor = EncryptionClient(
                    dataset_key_manager, person_key_manager, arguments["--input"], arguments["--output"])
                encryptor.decrypt(url)

            elif arguments["grant_access"]:
                requester_uuid = arguments["--requester"]
                requester_name = vault_client.read_entity_by_id(requester_uuid)
                    
                frdr_api_url = arguments["--frdr_api_url"]
                if frdr_api_url is None:
                    frdr_api_url = config.FRDR_API_BASE_URL
                frdr_api_client = FRDRAPIClient(base_url=frdr_api_url)

                dataset_uuid = arguments["--dataset"]
                dataset_title = frdr_api_client.get_dataset_title(dataset_uuid)
                
                if click.confirm("You are trying to grant requester {} access to dataset {}. Do you want to continue?".format(requester_name, dataset_title), default=False):
                    expire_date = arguments["--expire"]
                    dataset_key_manager = DatasetKeyManager(vault_client)
                    person_key_manager = PersonKeyManager(vault_client)
                    encryptor = EncryptionClient(
                        dataset_key_manager, person_key_manager)
                    encryptor.grant_access(
                        requester_uuid, dataset_uuid, expire_date)

                    # make api call to FRDR to put grant access info in db
                    frdr_api_client.login()
                    data = {"expires": expire_date, "vault_dataset_id": dataset_uuid,
                            "vault_requester_id": requester_uuid}
                    print(frdr_api_client.update_requestitem(data))

            elif arguments["show_vault_id"]:
                entity_id = vault_client.entity_id
                person_key_manager = PersonKeyManager(vault_client)
                # make sure there is a public key saved on Vault for the requester
                person_key_manager.create_or_retrieve_public_key()
                print(
                    "Please copy the following id to the Requester ID Field on the Access Request Page on FRDR.")
                print(Util.wrap_text(entity_id))

    except ValueError as ve:
        logger.error(ve)
    except Exception as e:
        logger.error("Exception caught, exiting. {}".format(e), exc_info=True)


if __name__ == "__main__":
    main()
