import os
import sys
import logging
from base64 import b64encode, b64decode
import textwrap
import subprocess
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from configparser import ConfigParser

logger = logging.getLogger("frdr-crypto.util")

class Util(object):
    
    @classmethod
    def make_dir(cls, dir_name):
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
            logger.info("A new directory {} created.".format(dir_name))
        else:
            logger.info("Creating a new directory {} failed, already existed.".format(dir_name))
            pass
   
    @classmethod
    def base64_to_byte(cls, plaintext):
        return b64decode(plaintext.encode())

    @classmethod
    def clean_dir_path(cls, path):
        if path.endswith(os.sep):
            return path[:-1]
        else:
            return path

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

        clean_logformatter = '%(asctime)s %(name)s [%(levelname)s] %(message)s'
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
            wrapped_text += '*{pad}{text:{width}}{pad}*\n'.format(text=line, pad=' '*padding, width=max_line_length)
        wrapped_text += 60 * '*'
        return wrapped_text

    @classmethod
    def send_email(cls, to_addr, msg_subject, msg_body_html, file_to_attach):    
        parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(parent_path, "email.ini")

        if os.path.exists(config_path):
            cfg = ConfigParser()
            cfg.read(config_path)
        else:
            logger.error("Email Server Config not found! Exiting!")
            sys.exit(1)
        
        host = cfg.get("smtp", "server")
        from_addr = cfg.get("smtp", "from_addr")
        
        message = MIMEMultipart("alternative")
        message["Subject"] = msg_subject
        message["From"] = from_addr
        message["To"] = to_addr
        message.attach(MIMEText(msg_body_html, "html"))

        with open(file_to_attach, 'rb') as f:
            # set attachment mime and file name, the image type is png
            mime = MIMEBase('image', 'png', filename='decrypt.png')
            # add required header data:
            mime.add_header('Content-Disposition', 'attachment', filename='decrypt.png')
            mime.add_header('X-Attachment-Id', '0')
            mime.add_header('Content-ID', '<0>')
            # read attachment file content into the MIMEBase object
            mime.set_payload(f.read())
            # encode with base64
            encoders.encode_base64(mime)
            # add MIMEBase object to MIMEMultipart object
            message.attach(mime)
    
        with smtplib.SMTP(host) as server:
            server.sendmail(from_addr, to_addr, message.as_string())
