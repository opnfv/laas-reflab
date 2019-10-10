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
from actions.actions import notify_ssh_access
import responses


class SSHNotificationTestCase(BaseActionTestCase):
    action_cls = notify_ssh_access.NotifySSHAction

    def setUp(self):
        super(SSHNotificationTestCase, self).setUp()
        self.action_service.set_value("lab_auth_token", "my_auth_token", local=False)
        self.action = self.get_action_instance(config={
            "dashboard": {
                "address": "http://my.dashboard.com",
                "lab_name": "my_lab"
            }
        })

    @responses.activate
    def test_notify_ssh_user(self):
        responses.add(responses.POST, "http://my.dashboard.com/api/labs/my_lab/jobs/1/task1")
        self.action.run(user="my_ssh_user", hosts=["my_host"], job_id=1, task_id="task1")
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], "my_auth_token")
        self.assertTrue("my_ssh_user" in responses.calls[0].request.body)
        self.assertTrue("my_host" in responses.calls[0].request.body)
