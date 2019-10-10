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

from lib.laas_api import DashboardAction


class NotifyIPMIAPIAction(DashboardAction):

    def run(self, ipmi_key=None, addr=None, mac=None, host=None):
        ipmi_pass = self.action_service.get_value(ipmi_key, local=False, decrypt=True)
        info = {
            'address': addr,
            'mac_address': mac,
            'pass': ipmi_pass,
            'type': "ipmi",
            'user': "OPNFV",
            'versions': ["2.0"]
        }

        endpoint = "/hosts/" + host + "/bmc"
        self.send_api_message(endpoint=endpoint, payload=info)
