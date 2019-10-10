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


class ManagementVlanAction(Action):

    def run(self, hosts):
        self.man_vlan = "98"
        self.ipmi_vlan = "99"
        commands = []
        for host_id in hosts:
            try:
                host = json.loads(self.action_service.get_value(host_id, local=False))
            except:
                print("cannot find host " + host_id)
                continue
            for interface in host['interfaces'].values():
                auth = json.loads(
                    self.action_service.get_value("switch_" + interface['switch'], local=False)
                )
                cmd = NXCommand(interface['switch'], auth)
                cmd.add_command("interface " + interface['port'])
                cmd.add_command("switchport mode trunk")
                cmd.add_command("switchport trunk allowed vlan " + ",".join([self.man_vlan, self.ipmi_vlan]))
                cmd.add_command("switchport trunk native vlan " + self.man_vlan)
                commands.append(cmd)
        for command in commands:
            print(command.execute())
