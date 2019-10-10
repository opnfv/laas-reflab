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

import json
from st2actions.runners.pythonrunner import Action


class ParseNetworkAction(Action):

    def run(self, task_data):
        task_data.pop("lab_token", None)  # We dont care, just remove if there
        if len(task_data) > 1:
            print("There should only be one host here!")
            return None

        ret = {
            'host': list(task_data.keys())[0],  # hostname
            'mappings': '+'.join(self.get_mappings(task_data)),  # mappings as understood by host task
            'default': self.get_default_interface(task_data),  # interface that should be def route
            'empty': self.detect_empty(task_data)
        }

        return ret

    def detect_empty(self, task_data):
        for hostname, iface_dict in task_data.items():
            for mac, vlan_list in iface_dict.items():
                if vlan_list:
                    return False
        return True

    def get_mappings(self, task_data):
        mappings = []
        for hostname, iface_dict in task_data.items():
            for mac, vlan_list in iface_dict.items():
                for vlan in vlan_list:
                    if vlan['tagged']:
                        mapping = mac + "-" + str(vlan['vlan_id'])
                        mappings.append(mapping)
        return mappings

    def get_default_vlans(self):
        vlan_list = json.loads(
            self.action_service.get_value("default_vlans", local=False)
        )
        return vlan_list

    def get_default_interface(self, task_data):
        default = set(self.get_default_vlans())
        for hostname, iface_dict in task_data.items():
            for mac, vlan_list in iface_dict.items():
                for vlan in vlan_list:
                    if int(vlan['vlan_id']) in default:
                        default_interface = mac
                        if vlan['tagged']:
                            default_interface += "." + str(vlan['vlan_id'])
                        return default_interface
