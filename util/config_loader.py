import yaml
import os

class Config:
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yml')) as yaml_config_file:
            self.config = yaml.safe_load(yaml_config_file)

    def __getattr__(self, name):
        return self.config[name]

config = Config()