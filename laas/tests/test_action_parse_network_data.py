##############################################################################
# Copyright 2019 Parker Berberian and Others                                 #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License");            #
# you may not use this file except in compliance with the License.           #
# You may obtain a copy of the License at                                    #
#                                                                            #
#    http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
##############################################################################
from st2tests.base import BaseActionTestCase

from actions.actions import parse_network_data


class ParseNetworkTestCase(BaseActionTestCase):
    action_cls = parse_network_data.ParseNetworkAction

    def setUp(self):
        super(ParseNetworkTestCase, self).setUp()
        self.action = self.get_action_instance()
        self.action.action_service.set_value("default_vlans", "[5, 10]", local=False)

    def test_empty_returns_true(self):
        data = {
            "host1": {
                "mac1": [],
                "mac2": []
            }
        }
        result = self.action.run(data)
        self.assertTrue(result['empty'])

    def test_single_vlan(self):
        data = {
            "host1": {
                "mac1": [{
                    "tagged": False,
                    "vlan_id": 10
                }],
                "mac2": []
            }
        }
        result = self.action.run(data)
        self.assertFalse(result['empty'])
        self.assertEqual("mac1", result['default'])
        self.assertEqual("host1", result['host'])
        # should be empty string because there are no tagged vlans to map
        self.assertFalse(result['mappings'])

    def test_single_tagged_vlan(self):
        data = {
            "host1": {
                "mac1": [{
                    "tagged": True,
                    "vlan_id": 10
                }],
                "mac2": []
            }
        }
        result = self.action.run(data)
        self.assertFalse(result['empty'])
        self.assertEqual("mac1.10", result['default'])
        self.assertEqual("host1", result['host'])
        self.assertEqual("mac1-10", result['mappings'])

    def test_complex_case(self):
        data = {
            "host1": {
                "mac1": [
                    {"tagged": True, "vlan_id": 50},
                    {"tagged": True, "vlan_id": 500},
                    {"tagged": False, "vlan_id": 100}
                ],
                "mac2": [
                    {"tagged": True, "vlan_id": 10},
                    {"tagged": False, "vlan_id": 1000}
                ]
            }
        }
        result = self.action.run(data)
        self.assertFalse(result['empty'])
        self.assertEqual("mac2.10", result['default'])
        self.assertEqual("host1", result['host'])
        mapping = set(result['mappings'].split("+"))
        expected = set(["mac1-50", "mac1-500", "mac2-10"])
        self.assertTrue(mapping.issubset(expected) and expected.issubset(mapping))
