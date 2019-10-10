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
from actions.actions import fog_captureHost
import responses
import json


class FogCaptureHostTestCase(BaseActionTestCase):
    action_cls = fog_captureHost.StartCaptureAction

    def setUp(self):
        super(FogCaptureHostTestCase, self).setUp()
        self.action = self.get_action_instance(config={
            "fog": {
                "address": "http://my.fog.com/fog/",
                "api_key": "my_api_key",
                "user_key": "my_user_key",
            }
        })

    def assertGoodHeader(self, request):
        self.assertEqual(request.headers['fog-api-token'], "my_api_key")
        self.assertEqual(request.headers['fog-user-token'], "my_user_key")
        # TODO: content type? only required when I send a body

    @responses.activate
    def test_fog_capture_host(self):
        responses.add(responses.POST, "http://my.fog.com/fog/host/42/task")
        self.action.action_service.set_value("host1", json.dumps({"fog_name": "fog_host1"}), local=False)
        responses.add(responses.GET, "http://my.fog.com/fog/host", json={
            "hosts": [
                {"name": "fog_host1", "id": 42},
            ]
        })
        self.action.run(host="host1")
        self.assertEqual(len(responses.calls), 2)
        self.assertGoodHeader(responses.calls[0].request)
        self.assertGoodHeader(responses.calls[1].request)
        self.assertEqual(json.loads(responses.calls[1].request.body), {"taskTypeID": 2})
