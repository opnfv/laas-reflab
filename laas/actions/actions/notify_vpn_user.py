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

from lib.laas_api import NotifyAction
import json


class NotifyVPNUserAction(NotifyAction):
    template = """
    Your VPN credentials:
        username: {{info.username}}
        password: {{info.password}}

    Instructions on how to connect to the UNH-IOL VPN can be found here:
    {{info.url}}
    """

    def run(self, vpn_key=None, job_id=None, task_id=None):
        vpn_info = json.loads(self.action_service.get_value(vpn_key, local=False, decrypt=True))
        info = {
            'username': vpn_info['username'],
            'password': vpn_info['password'],
            'url': "https://wiki.opnfv.org/display/INF/Lab-as-a-Service+at+the+UNH-IOL"
        }

        self.notify(self.template, info, job_id, task_id, lab_token=vpn_key)
