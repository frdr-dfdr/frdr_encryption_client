import datetime
import os
import re
import sys
import logging
from base64 import b64encode, b64decode
import textwrap
from pathlib import Path
from util.config_loader import config
import socket
import hashlib
import time
import pytz
import magic

logger = logging.getLogger("frdr-encryption-client.util")


class Util(object):

    @classmethod
    def make_dir(cls, dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
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
    
    @classmethod
    def path_tree(cls, path, generate_checksum=False):
        d = {'path': "/" + os.path.normpath(path), 'name': os.path.basename(path)}
        d['size'] = os.path.getsize(path)
        d['lastModified'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(path)))

        if os.path.isdir(path):
            d['path'] = d['path'] + "/"
            d['type'] = "dir"
            d['count'] = 1
            d['contents'] = [Util.path_tree(os.path.join(path,x), generate_checksum) for x in sorted(os.listdir(path))]
            for item in d['contents']:
                if item['type'] == "dir":
                    d['count'] = d['count'] + item['count']
                    d['size'] = d['size'] + item['size']
                else:
                    d['count'] = d['count'] + 1
                    d['size'] = d['size'] + item['size']
        else:
            d['type'] = "file"
            if generate_checksum:
                # Only generate checksum if file is 1 GB or less
                if d['size'] < 1024000000:
                    d['sha256'] = Util.compute_sha256(os.path.normpath(path))
                else:
                    d['sha256'] = 0

        return d

    @classmethod
    def compute_sha256(cls, file_name):
        # Read chunks of 4096 bytes for files
        CHUNK_SIZE = 4 * 1024
        hash_sha256 = hashlib.sha256()
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    @classmethod
    def generate_checksums(cls, input_path):
        """
        Crawl the submission generating checksums for each file 
        :param input_path: Relative path of publication.
        :return:
        """
        logger.info("Starting checksum generation")
        try:
            # Walk directory structure and generate checksums.
            sums_filename = 'frdr-checksums-and-filetypes-client.md'
            sums_fullpath = os.path.join(input_path, sums_filename)
            logger.info(f"Writing sums to {sums_fullpath}")
            if os.path.exists(sums_fullpath):
                os.remove(sums_fullpath)
            gendate = datetime.datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S %z %Z')
            hash_output_fp = open(sums_fullpath, 'w')
            hash_output_fp.write('## This file is automatically-generated by FRDR Encryption Application.\n')
            hash_output_fp.write(' It is not part of the submitted dataset. It contains file checksums and estimated file\n')
            hash_output_fp.write(' types for the submission to aid users of the dataset. \n\n')
            hash_output_fp.write(f"Date generated: {gendate} \n\n")
            hash_output_fp.write('## Ce fichier est généré automatiquement par FRDR Encryption Application.\n')
            hash_output_fp.write(' Il ne fait pas partie de l’ensemble de données soumis. Il contient les sommes de contrôle et le fichier estimé\n')
            hash_output_fp.write(' types pour la soumission à l’aide aux utilisateurs du jeu de données. \n\n')
            hash_output_fp.write(f"Date de génération: {gendate} \n\n")
            for dirpath, dirnames, filenames in os.walk(input_path):
                for filename in filenames:
                    if filename in config.EXCLUDED_FILES or filename == sums_filename:
                        continue
                    current_file = os.path.join(dirpath, filename)
                    checksum = Util.compute_sha256(current_file)
                    
                    try:
                        format_text = magic.from_file(current_file)
                    except magic.MagicException as e:
                        format_text = "unknown"
                        
                    relative_current_file_path = os.path.normpath(current_file.replace(input_path, ""))
                    hash_output_fp.write(f"**Filename/Fichier:** {relative_current_file_path} \n")
                    hash_output_fp.write(f"**SHA256 Checksum:/Sommes de contrôle** {checksum} \n")
                    hash_output_fp.write(f"**Estimated File Type/Le fichier estimé types:** {format_text} \n\n")
            hash_output_fp.close()
        except os.error as e:
            logger.error("Problems with generating sums and types file.")
            logger.exception(e)
            raise os.error 
        return sums_fullpath
