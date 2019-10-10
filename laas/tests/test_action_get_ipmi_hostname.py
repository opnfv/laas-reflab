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
from st2tests.base import BaseActionTestCase

from actions.actions import get_ipmi_hostname
import socket

hosts = {"host1": "ipmi_host1", "host2": "ipmi_host2"}


class IpmiHostnameActionTestCase(BaseActionTestCase):
    action_cls = get_ipmi_hostname.ipmi_infoAction

    def setUp(self):
        super(IpmiHostnameActionTestCase, self).setUp()
        self.skipTest("not read")

    def test_goodHostname_givesRightResult(self):
        action = self.get_action_instance()
        for key in hosts.keys():
            self.assertEquals(hosts[key], action.run(host=key))

    def test_results_resolvable(self):
        action = self.get_action_instance()
        for key in hosts.keys():
            # socket will return ip as a string if it can, which is truthy
            self.asserTrue(socket.gethostbyname(action.run(host=key)))

    def test_badHostname_throwsError(self):
        bad_host = "abc_I_dont_know_thee"
        action = self.get_action_instance()
        with self.assertRaises(IndexError):
            action.run(host=bad_host)
