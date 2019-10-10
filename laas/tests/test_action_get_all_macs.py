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
from actions.actions import get_all_macs
import json


class GetMacsTestCase(BaseActionTestCase):
    action_cls = get_all_macs.MacAction

    def setUp(self):
        super(GetMacsTestCase, self).setUp()
        self.action = self.get_action_instance()

    def test_single_mac(self):
        self.action.action_service.set_value("host1", json.dumps({
            "interfaces": {
                "mac1": {
                    "mac": "mac1",
                    "speed": 42
                }
            }
        }), local=False)
        result = self.action.run(host="host1")
        self.assertEqual(result, "mac1")

    def test_multiple_macs(self):
        self.action.action_service.set_value("host1", json.dumps({
            "interfaces": {
                "mac1": {
                    "mac": "mac1",
                    "speed": 42
                },
                "mac2": {
                    "mac": "mac2",
                    "speed": 42
                },
                "mac3": {
                    "mac": "mac3",
                    "speed": 42
                }
            }
        }), local=False)
        result = self.action.run(host="host1")
        parsed_results = set(result.split("|"))
        expected_results = set(["mac1", "mac2", "mac3"])
        self.assertTrue(
            parsed_results.issubset(expected_results) and expected_results.issubset(parsed_results)
        )
