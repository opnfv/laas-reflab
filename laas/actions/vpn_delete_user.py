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

import json
from vpnAction import VPNAction


class Del_VPN_User(VPNAction):

    def __init__(self, config=None):
        super(Del_VPN_User, self).__init__(config=config)

    def run(self, dn=None, key=None):
        if not dn or dn == "None":
            if not key or key == "None":
                return
            vpn_info = json.loads(
                    self.action_service.get_value(
                        name=key,
                        local=False,
                        decrypt=True
                        )
                    )
            dn = vpn_info['dn']
            st2key = key
        else:
            st2key = 'vpn_'
            # get username from dn
            for attr in dn.split(','):
                if 'uid' in attr:
                    st2key += attr.split('=')[-1]
        # we have the dn and key now
        self.action_service.delete_value(name=st2key, local=False)
        self.deleteUser(dn)
