##############################################################################
# Copyright 2017 Parker Berberian and Others                                 #
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

import datetime
import json
from lib.vpn import VPNAction


class Make_VPN_User(VPNAction):

    def __init__(self, config=None):
        super(Make_VPN_User, self).__init__(config=config)

    def run(self, user=None, passwd=None, job_id=None):
        if user == "None":
            user = None
        if passwd == "None":
            passwd = None
        name, passwd, dn = self.makeNewUser(name=user, passwd=passwd)
        vpn_info = {
            "dn": dn,
            "username": name,
            "password": passwd,
            "created": datetime.date.today().isoformat()
        }
        self.action_service.set_value(
            name='vpn_' + name,
            value=json.dumps(vpn_info),
            local=False,
            encrypt=True
        )
        if job_id and job_id != "None":
            self.addUserToJob(vpn_info, job_id)
        return "vpn_" + name

    def addUserToJob(self, vpn_info, job):
        name = "job_" + job
        job = json.loads(
            self.action_service.get_value(name, local=False)
        )
        if 'vpn_keys' not in job:
            job['vpn_keys'] = []
        job['vpn_keys'].append("vpn_" + vpn_info['username'])
        self.action_service.set_value(
            name=name,
            value=json.dumps(job),
            local=False
        )
