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
from actions.actions import detectHostsToBoot
import json
import responses


class DetectHostsTest(BaseActionTestCase):
    action_cls = detectHostsToBoot.DetectHostsAction

    def setUp(self):
        super(DetectHostsTest, self).setUp()
        # this is not documented
        self.action_service.set_value("lab_auth_token", "my_auth_token", local=False)
        self.action = self.get_action_instance(config={
            "dashboard": {
                "address": "http://my.dashboard.com",
                "lab_name": "my_lab"
            }
        })
        self.hosts_url = "http://my.dashboard.com/api/labs/my_lab/hosts/"
        self.action.action_service.set_value("hosts_to_boot", "[]", local=False)

    def hostDetected(self, host):
        detected_hosts = json.loads(self.action.action_service.get_value("hosts_to_boot", local=False))
        return host in detected_hosts

    @responses.activate
    def test_single_host_detected(self):
        self.action.action_service.set_value("hosts", '["host1"]', local=False)
        responses.add(responses.GET, self.hosts_url + "host1", json={"booked": True})
        self.action.run()
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], "my_auth_token")
        self.assertTrue(self.hostDetected("host1"))

    @responses.activate
    def test_single_host_not_detected(self):
        self.action.action_service.set_value("hosts", '["host1"]', local=False)
        responses.add(responses.GET, self.hosts_url + "host1", json={"booked": False})
        self.action.run()
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], "my_auth_token")
        self.assertEqual(self.action.action_service.get_value("hosts_to_boot", local=False), "[]")

    @responses.activate
    def test_multiple_hosts(self):
        self.action.action_service.set_value("hosts", '["host1", "host2", "host3"]', local=False)
        responses.add(responses.GET, self.hosts_url + "host1", json={"booked": True})
        responses.add(responses.GET, self.hosts_url + "host2", json={"booked": True})
        responses.add(responses.GET, self.hosts_url + "host3", json={"booked": False})

        self.action.run()
        self.assertEqual(len(responses.calls), 3)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], "my_auth_token")
        self.assertEqual(responses.calls[1].request.headers['auth-token'], "my_auth_token")
        self.assertEqual(responses.calls[2].request.headers['auth-token'], "my_auth_token")
        self.assertTrue(self.hostDetected("host1"))
        self.assertTrue(self.hostDetected("host2"))
        self.assertFalse(self.hostDetected("host3"))
