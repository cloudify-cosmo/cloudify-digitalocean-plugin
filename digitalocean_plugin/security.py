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
import random

import requests

from cloudify.exceptions import NonRecoverableError


class DigitalOceanSecurity(object):

    pubkey_stub = "Cloudify Key {0}"
    api_endpoint = 'https://api.digitalocean.com/v2/'
    token_file_name = 'token.txt'
    key_count_limit = 1024

    def __init__(self):
        self.digitalocean_security_token \
            = self.load_digitalocean_account_token()
        self.rand = random

    def build_url(self, end_of_url):
        return "%s%s" % (self.api_endpoint, end_of_url.replace("//", "/"))

    def common_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': "Bearer %s" % self.digitalocean_security_token
        }

    def delete_pubkey_from_account_by_fingerprint(self, fingerprint, **_):
        pass

    def delete_pubkey_from_account_by_keyid(self, keyid, **_):
        """
        :param keyid: id assigned to key (when imported) by digital ocean
        :param _: varargs
        :return: True always
        """
        pass

    def add_pubkey_to_digitalocean_account(self, pubkey_file, key_name, **_):
        """
        Uploads a public key file to the DigitalOcean account.
        :param pubkey_file: full path to a public key file
        :param name: an optional name for your key - will be assigned randomly
         if not provided
        :param _:
        :return: The id and fingerprint of the uploaded key, returned as a
        tuple (id, fingerprint)
        """
        if not os.path.isfile(pubkey_file):
            raise NonRecoverableError("Unknown public key file: '{0}'."
                                      .format(pubkey_file))
        with open(pubkey_file, 'r') as f:
            pubkey = f.read()
        key_name = self.make_key_name(key_name)
        assert pubkey, "A non-empty public key file must be provided."

        payload = {
            "name": key_name,
            "public_key": pubkey
        }

        url = self.build_url('account/keys')
        h = self.common_headers()

        try:
            # because it's a POST, it should be only 1 response
            # if we were to call GET, it would return all associated keys
            response = requests.post(url, headers=h, data=payload)
            code = response.status_code
            if code < 200 or code > 299:
                raise NonRecoverableError(
                    "Error on server for %(URL)s. Status code = '%(CODE)d'."
                    % {'URL': url, 'CODE': code}
                )
            r = response.json()['ssh_key']

        except (KeyError, ValueError):
            raise NonRecoverableError(
                "Error adding public ssh key to DigitalOcean account.")

        return r['id'], r['fingerprint']

    def make_key_name(self, proposed_name):
        """
        :param proposed_name: a name to test for emptiness
        :return: proposed_name, stripped (if non-empty), else a
        randomly-generated name
        """
        if proposed_name:
            return proposed_name.strip()
        r = self.rand.randint(0, self.key_count_limit + 1)
        return self.pubkey_stub.format(r)

    def cache_pubkey_copy_from_digitalocean_account(self,
                                                    fingerprint, **_):

        raise NonRecoverableError("Not implemented yet.")

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

        token_path = os.path.join(cwd(), self.token_file_name)
        if not os.path.isfile(token_path):
            raise NonRecoverableError('Missing security token file "%s".'
                                      % token_path)
        with open(token_path, 'r') as f:
            return f.read()
