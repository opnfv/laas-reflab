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
from actions.actions import network_task
import json
import mock


class NetworkTaskTest(BaseActionTestCase):
    action_cls = network_task.PodNetworkManagerAction

    def setUp(self):
        super(NetworkTaskTest, self).setUp()
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

    def assertInterfaceConfigured(self, mocked_object, config):
        all_calls = mocked_object.add_command.call_args_list
        all_args = [c[0][0] for c in all_calls]
        # first, we set the interface context
        self.assertEqual(all_args[0], "interface " + config[0]['port'])
        # next, the port must be trunked
        self.assertEqual(all_args[1], "switchport mode trunk")
        # next, check that the correct vlans are added
        vlan_cmd = all_args[2]
        self.assertTrue(vlan_cmd.startswith("switchport trunk allowed vlan "))
        parsed = vlan_cmd.split(" ")
        self.assertEqual(len(parsed), 5)
        expected_vlans = set([98, 99])
        for vlan in config:
            expected_vlans.add(vlan['vlan_id'])

        requested_vlans = parsed[-1].split(",")
        requested_vlans = set([int(v) for v in requested_vlans])
        self.assertEqual(requested_vlans, expected_vlans)
        # TODO: native vlan
        # TODO: assert executed

    def test_simple_net_config(self):
        with mock.patch('actions.actions.network_task.NXCommand') as Mocked:
            mocks = []
            for i in range(2):
                mocks.append(mock.Mock())
            Mocked.side_effect = mocks

            net_conf = {
                "host1": {
                    "mac1": [{"tagged": True, "vlan_id": 100}],
                    "mac2": [{"tagged": False, "vlan_id": 10}],
                }
            }
            self.action.run(net_conf)

            Mocked.assert_any_call("switch1", {"user": "user", "password": "password"})
            config_map = {
                "Ethernet1/1": [{"tagged": True, "vlan_id": 100, "port": "Ethernet1/1"}],
                "Ethernet1/2": [{"tagged": False, "vlan_id": 10, "port": "Ethernet1/2"}],
            }
            for mocked_cmd in mocks:
                target_iface = mocked_cmd.add_command.call_args_list[0][0][0].split(" ")[-1]
                self.assertInterfaceConfigured(mocked_cmd, config_map[target_iface])
