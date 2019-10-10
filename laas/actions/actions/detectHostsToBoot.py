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
import json
import requests


class DetectHostsAction(Action):
    def __init__(self, *args, **kwargs):
        self._config = kwargs.get('config', None)
        super(DetectHostsAction, self).__init__(*args, **kwargs)

        server = self._config['dashboard']['address']
        name = self._config['dashboard']['lab_name']
        auth = self.action_service.get_value("lab_auth_token", local=False)

        self.base_url = server + "/api/labs/" + name + "/hosts/"
        self.header = {"auth-token": auth}

    def run(self):
        hosts_to_boot = set()
        my_hosts = json.loads(
            self.action_service.get_value(name="hosts", local=False)
        )
        for host in my_hosts:
            if self.is_booked(host):
                hosts_to_boot.add(host)
        self.action_service.set_value(name="hosts_to_boot", value=json.dumps(list(hosts_to_boot)), local=False)

    def is_booked(self, hostname):
        url = self.base_url + hostname

        try:
            response = requests.get(url, timeout=10, headers=self.header)
            return response.json()['booked']
        except:
            self.logger.exception("Something happened..")
            return True  # return true on failure to be safe
