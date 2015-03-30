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
import os
import testtools

import responses

from cloudify.mocks import MockCloudifyContext
from cloudify.exceptions import NonRecoverableError

from digitalocean_plugin.security import DigitalOceanSecurity


class TestSecurity(testtools.TestCase):

    test_pubkey_filename = 'testkey.pub'
    badkey_path = 'xyzpdq.pub'

    test_instance = DigitalOceanSecurity()

    @staticmethod
    def mock_ctx(test_name):

        test_node_id = test_name
        test_properties = {}

        ctx = MockCloudifyContext(node_id=test_node_id,
                                  properties=test_properties)

        return ctx

    @staticmethod
    def make_url(end_of_url):
        return "https://api.digitalocean.com/v2/%s" % end_of_url

    @staticmethod
    def load_response(fixture_filename):

        cwd = os.path.dirname(__file__)
        fix_path = "%s/fixtures/" % cwd
        fixture_file_path = os.path.join(fix_path, fixture_filename)

        if not os.path.isfile(fixture_file_path):
            raise AssertionError(
                "No such fixture file: %s ." % fixture_file_path)

        with open(fixture_file_path, 'r') as fix:
            return fix.read()

    @responses.activate
    def test_add_pubkey_to_digitalocean_account(self):

        ctx = self.mock_ctx('test_add_pubkey_to_digitalocean_account')

        # raising when garbage input is provided
        oops = self.assertRaises(NonRecoverableError,
                                 self.test_instance
                                 .add_pubkey_to_digitalocean_account,
                                 self.badkey_path,
                                 None,
                                 ctx=ctx)
        self.assertIn("Unknown public key file: '{0}'."
                      .format(self.badkey_path), oops.message)

        pubkey_path = os.path.join(os.path.dirname(__file__),
                                   self.test_pubkey_filename)

        responses.add(responses.POST,
                      self.make_url('account/keys'),
                      self.load_response('account.keys.json'))

        result = self.test_instance.add_pubkey_to_digitalocean_account(
            pubkey_path,
            None,
            ctx=ctx)

        self.assertEqual(512190, result[0])

        result_fingerprint = result[1]
        self.assertEqual(47, len(result_fingerprint))
        expected_fingerprint \
            = '3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa'
        self.assertEqual(expected_fingerprint, result_fingerprint)

    def test_make_key_name(self):

        test_input = "a key name"
        self.assertEqual(self.test_instance.make_key_name(test_input),
                         test_input)

        strip_me = " key "
        actual = self.test_instance.make_key_name(strip_me)
        self.assertEqual(actual, strip_me.strip())

        actual0 = self.test_instance.make_key_name(None)
        self.assertEqual(actual0 is None, False,
                         "Generated key name should be non-None.")

        actual1 = self.test_instance.make_key_name(None)
        actual2 = self.test_instance.make_key_name(None)

        self.assertEqual(actual1 == actual2, False,
                         "Generated key names should be different.")

    def test_build_url(self):

        hi_mom = 'hi/mom'

        act = self.test_instance.build_url(hi_mom)
        self.assertEqual(True, act.endswith(hi_mom))
        self.assertEqual(act, "https://api.digitalocean.com/v2/hi/mom")

        act = self.test_instance.build_url("/%s" % hi_mom)
        self.assertEqual(True, act.endswith(hi_mom))
        self.assertEqual(False, act.startswith("/"))

        act = self.test_instance.build_url("/////%s" % hi_mom)
        self.assertEqual(True, act.endswith(hi_mom))
        self.assertEqual(False, act.startswith("/"))

    def test_common_headers(self):

        act = self.test_instance.common_headers()

        self.assertEqual('application/json', act['Content-Type'],
                         "Json should be specified as the "
                         "preferred content type.")
        auth = act['Authorization']
        self.assertEqual(True, auth.startswith('Bearer '))
        self.assertEqual(True, auth.endswith(
            self.test_instance.digitalocean_security_token))
