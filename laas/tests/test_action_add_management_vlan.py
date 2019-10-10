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
from actions.actions import add_management_vlan
import json
import mock


class ManagementVlanTest(BaseActionTestCase):
    action_cls = add_management_vlan.ManagementVlanAction

    def setUp(self):
        super(ManagementVlanTest, self).setUp()
        self.action = self.get_action_instance()
        host_info = {
            "interfaces": {
                "mac1": {
                    "mac": "mac1",
                    "bus": "bus1",
                    "switch": "switch1",
                    "port": "Ethernet1/1",
                    "name": "ifname1"
                },
                "mac2": {
                    "mac": "mac2",
                    "bus": "bus2",
                    "switch": "switch1",
                    "port": "Ethernet1/2",
                    "name": "ifname2"
                }
            }
        }
        self.action.action_service.set_value("host1", json.dumps(host_info), local=False)
        switch_info = {"user": "user", "password": "password"}
        self.action.action_service.set_value("switch_switch1", json.dumps(switch_info), local=False)

    def hasConsecutiveCalls(self, args, mock_obj):
        """
        args is a list of arguments as tuples. This method asserts that
        mock was called with those arguments in that order
        """
        if len(args) < 1:
            return True
        for call_index in range(len(mock_obj.call_args_list)):
            arg_index = 0
            while mock_obj.call_args_list[call_index] == (args[arg_index],):
                call_index += 1
                arg_index += 1
                if arg_index == len(args):
                    return True
        return False

    def test_vlans(self):
        with mock.patch('actions.actions.add_management_vlan.NXCommand') as Mocked:
            self.action.run(["host1"])
            self.assertTrue(Mocked.called)

            # assert that the correct commands are run in order for each interface
            # but we dont care about the order of the interfaces
            mocked = Mocked.return_value
            self.assertTrue(mocked.add_command.called)
            expected_calls = [
                ("interface Ethernet1/1",),
                ("switchport mode trunk",),
                ("switchport trunk allowed vlan 98,99",),
                ("switchport trunk native vlan 98",),
            ]
            self.assertTrue(self.hasConsecutiveCalls(expected_calls, mocked.add_command))

            expected_calls[0] = ("interface Ethernet1/2",)
            self.assertTrue(self.hasConsecutiveCalls(expected_calls, mocked.add_command))

            self.assertEqual(mocked.add_command.call_count, 8)
            self.assertEqual(Mocked.call_count, mocked.execute.call_count)
