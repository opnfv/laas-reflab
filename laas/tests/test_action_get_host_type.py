##############################################################################
# Copyright 2019 Parker Berberian and Others                                 #
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
from actions.actions import get_host_type


class FinishTaskTestCase(BaseActionTestCase):
    action_cls = get_host_type.HostTypeAction

    def setUp(self):
        super(FinishTaskTestCase, self).setUp()
        self.action = self.get_action_instance()

    def test_hpe_host_type(self):
        result = self.action.run(host="hpe5")
        self.assertEqual(result, "hpe")

    def test_arm_host_type(self):
        result = self.action.run(host="arm50")
        self.assertEqual(result, "arm")

    def test_bad_host_type(self):
        result = self.action.run(host="unknown")
        self.assertFalse(result)
