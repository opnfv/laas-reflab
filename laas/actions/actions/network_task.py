##############################################################################
# Copyright 2018 Parker Berberian and Others                                 #
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

from st2actions.runners.pythonrunner import Action
from lib.cisco import NXCommand
import json


class PodNetworkManagerAction(Action):

    def parse_net_config(self, net_config):
        """
        Meaty method to ultimately get a list of NXCommands that need to be run
        to fulfill the requested config
        """
        commands = []
        for hostId in net_config.keys():
            host = json.loads(self.action_service.get_value(hostId, local=False))
            interfaces = net_config[hostId]
            configured_switches = set()  # place to remember which switches we have modified
            for interface_name in interfaces.keys():
                interface = host['interfaces'][interface_name]
                auth = json.loads(self.action_service.get_value("switch_" + interface['switch'], local=False))
                cmd = NXCommand(interface['switch'], auth)
                cmd.add_command("interface " + interface['port'])
                cmd.add_command("switchport mode trunk")
                native_vlan = None
                allowed_vlans = set(["99", "98"])  # always allow ipmi vlan TODO config
                vlans = interfaces[interface_name]
                for vlan in vlans:
                    allowed_vlans.add(str(vlan['vlan_id']))
                    if not vlan['tagged']:
                        native_vlan = str(vlan['vlan_id'])
                vlan_str = "none"
                if len(allowed_vlans) > 0:
                    vlan_str = ",".join(allowed_vlans)
                cmd.add_command("switchport trunk allowed vlan " + vlan_str)
                if native_vlan:
                    cmd.add_command("switchport trunk native vlan " + native_vlan)
                cmd.add_command("copy run start")
                commands.append(cmd)

                if interface['switch'] not in configured_switches:
                    save_cmd = NXCommand(interface['switch'], auth)
                    save_cmd.add_command("copy run start")
                    commands.append(save_cmd)
                    configured_switches.add(interface['switch'])

        return commands

    def run(self, network_data):
        network_data.pop("lab_token", None)
        self.commands = self.parse_net_config(network_data)
        for cmd in self.commands:
            print(cmd.execute())
