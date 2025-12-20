#
# Copyright (c) 2024 Digital Research Alliance of Canada
#
# This file is part of FRDR Encryption Application.
#
# FRDR Encryption Application is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the FRDR Encryption Application Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# FRDR Encryption Application is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRDR Encryption Application. If not, see <https://www.gnu.org/licenses/>.
#

import os
import logging
from util.util import Util
from util.configLoader import config
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography import x509


class PersonKeyManager(object):
    def __init__(self, vault_client):
        """Class init function

        Args:
            vault_client (VaultClient): Wrapper of HashiCorp Vault API client
        """
        self._logger = logging.getLogger(
            "frdr-encryption-application.person-key-manager.vault")
        self._vault_client = vault_client
        self._public_key = None

    def generate_certificate(self):
        """Use HashiCorp Vault's PKI secrets engine to generate a new 
           set of credentials (certificate and private key).

        Returns:
            tuple(string, bytes): certificate and private key
        """
        certificate, private_key_str = self._vault_client.generate_certificate(
            name=config.VAULT_GENERATE_CERT_ROLE_NAME,
            common_name=config.VAULT_GENERATE_CERT_COMMON_NAME,
            mount_point=config.VAULT_GENERATE_CERT_MOUNT_NAME
        )
        private_key = private_key_str.encode()
        return (certificate, private_key)

    def save_key_locally(self, key, filename):
        """Save the key to the local machine at the given path.

        Args:
            key (bytes): The key to save
            filename (string): The path which the key is saved at locally
        """
        with open(filename, 'wb') as f:
            f.write(key)
        self._logger.info("Key is saved to local path {}".format(filename))

    def read_private_key(self, filename):
        """Read the private key from the local machine at the given path

        Args:
            filename (string): The path where the private key is saved at

        Returns:
            bytes: The private key in bytes
        """
        with open(filename, "rb") as f:
            private_key = f.read()
        self._logger.info(
            "Private key is read from local path {}".format(filename))
        return private_key

    def read_public_key_locally(self, filename):
        """Read the public key from the local machine at the given path

        Args:
            filename (string): The path where the public key is saved at

        Returns:
            bytes: The public key in bytes
        """
        with open(filename, "rb") as f:
            public_key = f.read()
        self._logger.info(
            "Public key is read from local path {}".format(filename))
        return public_key

    def extract_public_key_from_cert(self, cert):
        """Extract the public key from the certificate

        Args:
            cert (string): The certificate

        Returns:
            bytes: The public key in bytes
        """
        certificate = x509.load_pem_x509_certificate(
            cert.encode(),
            backend=default_backend()
        )
        public_key = certificate.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_key

    def save_public_key_to_vault(self, public_key):
        """Save the public key to the key server. The path on the key
           server is generated in the function. 

        Args:
            public_key (bytes): The public key in bytes
        """
        path = "/".join([config.VAULT_PUBLIC_KEY_PATH,
                        self.get_vault_entity_id()])
        if isinstance(public_key, bytes):
            public_key = Util.byte_to_base64(public_key)
        self._vault_client.save_key_to_vault(path, public_key)

    def read_public_key_from_vault(self, user_entity_id):
        try:
            path = "/".join([config.VAULT_PUBLIC_KEY_PATH, user_entity_id])
            return self._vault_client.retrive_key_from_vault(path)
        except Exception as e:
            self._logger.error(
                "Failed to read public key from Vault. {}".format(e))
            return None

    def get_vault_entity_id(self):
        """Get the logged in user's ID on the key server

        Returns:
            string: The logged in user's ID on the key server
        """
        return self._vault_client.entity_id

    def create_or_retrieve_public_key(self):
        """Read the public key from the key server if existing. Otherwise, 
           create a private public key pair, save them locally and save 
           the public key to the key server. 

        Raises:
            ValueError: If the local public key is not the same as the public 
            key saved on the key server. 

        Returns:
            string: The public key for the logged in user
        """
        public_key_on_vault = self.read_public_key_from_vault(
            self.get_vault_entity_id())

        # If there is no public key saved on Vault, a new pair of keys is generated and saved locally, and the public
        # key is saved on Vault
        if public_key_on_vault is None:
            self._logger.info(
                "No public key is saved on Vault for the current user, generating a pair of public and private key")
            cert, private_key = self.generate_certificate()
            private_key_path = os.path.join(Util.get_key_dir(
                self.get_vault_entity_id()), config.LOCAL_PRIVATE_KEY_FILENAME)
            self.save_key_locally(private_key, private_key_path)
            public_key = self.extract_public_key_from_cert(cert)
            public_key_path = os.path.join(Util.get_key_dir(
                self.get_vault_entity_id()), config.LOCAL_PUBLIC_KEY_FILENAME)
            self.save_key_locally(public_key, public_key_path)
            self.save_public_key_to_vault(public_key)
            return public_key
        else:
            # Check if public key saved on Vault is the same as the public key saved locally.
            # If not, raise ValueError
            public_key_path = os.path.join(Util.get_key_dir(self.get_vault_entity_id()), config.LOCAL_PUBLIC_KEY_FILENAME)
            public_key_local = self.read_public_key_locally(public_key_path)
            if isinstance(public_key_local, bytes):
                public_key_local = Util.byte_to_base64(public_key_local)
            if public_key_local != public_key_on_vault:
                raise ValueError("The public key saved locally does not match the key saved on Vault.")
            return public_key_on_vault
    
    def get_public_key(self):
        """Get the public key without creating a new key pair
        
        Returns:
            bytes: The public key in PEM format (bytes), or None if not found
        
        Raises:
            ValueError: If public keys don't match between vault and local
        """
        public_key_on_vault = self.read_public_key_from_vault(
            self.get_vault_entity_id())
        
        # Convert vault public key to bytes if it exists
        if public_key_on_vault is not None:
            public_key_on_vault = Util.base64_to_byte(public_key_on_vault)
        
        public_key_path = os.path.join(Util.get_key_dir(
            self.get_vault_entity_id()), config.LOCAL_PUBLIC_KEY_FILENAME)
        
        # Read local public key
        public_key_local = None
        if os.path.exists(public_key_path):
            public_key_local = self.read_public_key_locally(public_key_path)
            # Ensure it's bytes
            if not isinstance(public_key_local, bytes):
                public_key_local = public_key_local.encode('utf-8')
        
        # Case 1: Both vault and local have public keys
        if public_key_on_vault is not None and public_key_local is not None:
            if public_key_local != public_key_on_vault:
                raise ValueError("The public key saved locally does not match the key saved on Vault.")
            self._logger.info("Public key found on both vault and local, and they match")
            return public_key_on_vault
        
        # Case 2: Only local has public key, vault doesn't
        elif public_key_local is not None and public_key_on_vault is None:
            self._logger.info("Public key found locally but not on vault, saving to vault")
            # Convert to base64 for vault storage
            public_key_local_base64 = Util.byte_to_base64(public_key_local)
            self.save_public_key_to_vault(public_key_local_base64)
            return public_key_local
        
        # Case 3: Only vault has public key, local doesn't
        elif public_key_on_vault is not None and public_key_local is None:
            self._logger.info("Public key found on vault but not locally, saving locally")
            self.save_key_locally(public_key_on_vault, public_key_path)
            return public_key_on_vault
        
        # Case 4: Neither vault nor local has public key
        else:
            self._logger.warning("No public key found on vault or locally")
            return None

    @property
    def my_public_key(self):
        """Return the logged in user's public key. 

        Returns:
            string: The public key for the logged in user
        """
        if self._public_key is None:
            self._public_key = self.create_or_retrieve_public_key()
        return self._public_key
