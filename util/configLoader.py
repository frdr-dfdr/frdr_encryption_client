#
# Copyright (c) 2024 Digital Research Alliance of Canada
#
# This file is part of FRDR Encryption Application.
#
# FRDR Encryption Application is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the FRDR Encryption Application Software Foundation,
# version 3 of the License.
#
# FRDR Encryption Application is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar. If not, see <https://www.gnu.org/licenses/>.
#

import yaml
import os

class Config:
    def __init__(self):
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yml')) as yaml_config_file:
            self.config = yaml.safe_load(yaml_config_file)

    def __getattr__(self, name):
        return self.config[name]

config = Config()