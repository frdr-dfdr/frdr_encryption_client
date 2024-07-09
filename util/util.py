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
# along with Foobar. If not, see <https://www.gnu.org/licenses/>.
#

import os
import re
import sys
import logging
from base64 import b64encode, b64decode
import textwrap
from pathlib import Path
from util.configLoader import config
import socket

logger = logging.getLogger("frdr-encryption-client.util")


class Util(object):

    @classmethod
    def make_dir(cls, dir_name):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
            logger.info("A new directory {} created.".format(dir_name))
        else:
            logger.info(
                "Creating a new directory {} failed, already existed.".format(dir_name))

    @classmethod
    def base64_to_byte(cls, plaintext):
        return b64decode(plaintext.encode())

    @classmethod
    def byte_to_base64(cls, byte):
        return b64encode(byte).decode()

    @classmethod
    def clean_dir_path(cls, path):
        if path.endswith(os.sep):
            return path[:-1]
        else:
            return path

    @classmethod
    def get_key_dir(cls, subdir):
        home = str(Path.home())
        key_dir = os.path.join(home, config.LOCAL_KEY_DIR_NAME, subdir)
        if not os.path.exists(key_dir):
            Util.make_dir(key_dir)
        return key_dir

    @classmethod
    def check_dir_exists(cls, path):
        return os.path.isdir(path)

    @classmethod
    def check_file_exists(cls, path):
        return os.path.isfile(path)

    @classmethod
    def get_logger(cls, name, log_level="INFO", filepath=None):
        logger = logging.getLogger(name)
        # if logger already exists, return it
        if logger.handlers:
            return logger

        level = getattr(logging, log_level.upper() if log_level else "INFO")
        try:
            logger.setLevel(level)
        except:
            logger.setLevel(logging.INFO)

        logger.info("Log level: {}".format(log_level))
        clean_logformatter = '%(asctime)s %(name)s [%(levelname)s] %(message)s [%(filename)s:%(lineno)d][Process ID: %(process)s]'
        clean_formatter = logging.Formatter(clean_logformatter)
        console = logging.StreamHandler(sys.stdout)
        try:
            console.setLevel(level)
        except:
            console.setLevel(logging.INFO)

        # console.addFilter(lambda record: record.levelno <= logging.INFO)
        console.setFormatter(clean_formatter)
        logger.addHandler(console)

        # Create handlers
        if filepath:
            logformatter = '%(asctime)s %(name)s [%(levelname)s] %(message)s'
            formatter = logging.Formatter(logformatter, '%Y-%m-%d %H:%M:%S')
            file_handler = logging.FileHandler(filepath, encoding='utf-8')
            try:
                file_handler.setLevel(level)
            except:
                file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    @classmethod
    def wrap_text(cls, text):
        padding = 3  # 3 spaces from left and right
        max_line_length = 58 - padding * 2  # 58 because 60 - 2*asterisks
        lines = textwrap.wrap(text, max_line_length)
        wrapped_text = 60 * '*' + '\n'
        for line in lines:
            wrapped_text += '*{pad}{text:{width}}{pad}*\n'.format(
                text=line, pad=' '*padding, width=max_line_length)
        wrapped_text += 60 * '*'
        return wrapped_text

    @classmethod
    def find_free_port(cls,
                       port=config.VAULT_CLIENT_LOGIN_REDIRECT_PORT_MIN,
                       max_port=config.VAULT_CLIENT_LOGIN_REDIRECT_PORT_MAX):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while port <= max_port:
            try:
                sock.bind(('127.0.0.1', port))
                sock.close()
                return port
            except OSError:
                port += 1
        raise IOError("The app needs to use a port between {} and {} for login process. \
                        Please free a port."
                      .format(config.VAULT_CLIENT_LOGIN_REDIRECT_PORT_MIN, config.VAULT_CLIENT_LOGIN_REDIRECT_PORT_MAX))

    @classmethod
    def parse_url(cls, url):
        match = re.match(
            r"^.*secret/data/dataset/([0-9a-f\-]*)/([0-9a-f\-]*)/?(.*)?", url)
        depositor_uuid = match.group(1)
        dataset_uuid = match.group(2)
        requester_uuid = match.group(3)
        return (depositor_uuid, dataset_uuid, requester_uuid)