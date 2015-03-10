# #######
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from cloudify.exceptions import NonRecoverableError


class DigitalOceanSecurity(object):

    def __init__(self):
        self.digitalocean_security_token \
            = self.load_digitalocean_account_token()
        self.api_endpoint = "https://api.digitalocean.com/v2/"

    def delete_pubkey_from_digitalocean_account(self, fingerprint, **_):
        pass

    def add_pubkey_to_digitalocean_account(self, alias, pubkey_file, **_):
        fingerprint = '43:51:43:a1:b5:fc:8b:b7:0a:3a:a9:b1:0f:66:73:a8'
        print self
        if not os.path.isfile(pubkey_file):
            raise NonRecoverableError("Unknown public key file '{0}'."
                                      .format(pubkey_file))

        return fingerprint

    def cache_pubkey_copy_from_digitalocean_account(self,
                                                    fingerprint, **_):
        pass

    def load_digitalocean_account_token(self, **_):
        """
        This will load a security token from a local file called token.txt. A
        token can be obtained from DigitalOcean by Registering a New
        Developer or Authorized Application.
        :return: the security token, as a string
        :raises: NonRecoverableError if token.txt file is not present
        """
        def cwd():
            return os.path.dirname(__file__)
        print self

        token_path = os.path.join(cwd(), 'token.txt')
        if not os.path.isfile(token_path):
            raise NonRecoverableError('Missing security token file "%s".'
                                      % token_path)
        with open(token_path, 'r') as f:
            return f.read()
