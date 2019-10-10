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
from actions.actions import notify_ipmi_user
import responses


class IPMINotificationTestCase(BaseActionTestCase):
    action_cls = notify_ipmi_user.NotifyIPMIUserAction

    def setUp(self):
        super(IPMINotificationTestCase, self).setUp()
        self.action_service.set_value("lab_auth_token", "my_auth_token", local=False)
        self.action = self.get_action_instance(config={
            "dashboard": {
                "address": "http://my.dashboard.com",
                "lab_name": "my_lab"
            }
        })

    @responses.activate
    def test_notify_ipmi_user(self):
        responses.add(responses.POST, "http://my.dashboard.com/api/labs/my_lab/jobs/1/task1")
        self.action.action_service.set_value("my_ipmi_key", "my_ipmi_password", local=False)
        self.action.run(ipmi_key="my_ipmi_key", hostname="my_host", addr="my_ipmi_addr", job_id=1, task_id="task1")
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], "my_auth_token")
        self.assertTrue("my_ipmi_addr" in responses.calls[0].request.body)
        self.assertTrue("my_host" in responses.calls[0].request.body)
        self.assertTrue("my_ipmi_password" in responses.calls[0].request.body)
