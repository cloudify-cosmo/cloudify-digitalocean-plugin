########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
import testtools

import os

from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError

from digitalocean_plugin.security import DigitalOceanSecurity


class TestSecurity(testtools.TestCase):

    test_keypair_alias = "my-little-keypair"
    test_pubkey_file = "testkey.pub"
    badkey_path = 'xyzpdq.pub'

    test_instance = DigitalOceanSecurity()

    def mock_ctx(self, test_name):

        test_node_id = test_name
        test_properties = {}

        ctx = MockCloudifyContext(node_id=test_node_id,
                                  properties=test_properties)

        return ctx

    def test_add_pubkey_to_digitalocean_account(self):

        ctx = self.mock_ctx("test_add_pubkey_to_digitalocean_account")

        oops = self.assertRaise(NonRecoverableError,
                                self.test_instance
                                .add_pubkey_to_digitalocean_account(
                                    self.test_keypair_alias, self.badkey_path,
                                    ctx=ctx))
        self.assertIn("Unknown public key file '{0}'".format(self.badkey_path),
                      oops.message)

        pubkey_path = os.path.join(os.path.dirname(__file__),
                                   self.test_pubkey_file)

        result = self.test_instance.add_pubkey_to_digitalocean_account(
            self.test_keypair_alias, pubkey_path, ctx=ctx)

        self.assertEquals(47, len(result))
        self.assertEquals("", result)

        pass
