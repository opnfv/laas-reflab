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
from actions.actions import get_ipmi_password

hosts = ["ipmi_hostname1", "ipmi_hostname2"]


class IpmiPasswordActionTestCase(BaseActionTestCase):
    action_cls = get_ipmi_password.ipmi_passwdAction

    def setUp(self):
        super(IpmiPasswordActionTestCase, self).setUp()
        self.skipTest("not read")

    def test_goodHost_returnsValue(self):
        action = self.get_action_instance()
        for host in hosts:
            self.assertTrue(action.run(host=host))

    def test_badHost_throwsError(self):
        bad_host = "abc_IDontKnowThee"
        action = self.get_action_instance()
        with self.assertRaises(IndexError):
            action.run(host=bad_host)
