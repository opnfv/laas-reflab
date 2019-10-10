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
from actions.actions.lib import fog
import responses
import json


class FogTestCase(BaseActionTestCase):
    action_cls = fog.FogAction

    def setUp(self):
        super(FogTestCase, self).setUp()
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
    def test_fog_create_image(self):
        responses.add(responses.POST, "http://my.fog.com/fog/image")
        payload = {"key1": "v1", "key2": "v2"}
        self.action.createImage(payload)
        self.assertEqual(len(responses.calls), 1)
        self.assertGoodHeader(responses.calls[0].request)
        self.assertEqual(payload, json.loads(responses.calls[0].request.body))

    @responses.activate
    def test_fog_get_image(self):
        payload = {
            "id": 42,
            "key": "value",
            "name": "fakeImage"
        }
        responses.add(responses.GET, "http://my.fog.com/fog/image/42", json=payload)
        result = self.action.getImage(img=42)
        self.assertEqual(len(responses.calls), 1)
        self.assertGoodHeader(responses.calls[0].request)
        self.assertEqual(result, payload)

    @responses.activate
    def test_fog_delete_task(self):
        responses.add(responses.DELETE, "http://my.fog.com/fog/fog/host/42/cancel")
        self.action.delTask(42)
        self.assertEqual(len(responses.calls), 1)
        self.assertGoodHeader(responses.calls[0].request)

    @responses.activate
    def test_get_host_number(self):
        payload = {
            "hosts": [
                {"name": "host1", "id": 1},
                {"name": "host2", "id": 2},
                {"name": "host3", "id": 3},
                {"name": "host4", "id": 4},
                {"name": "host5", "id": 5},
            ]
        }
        responses.add(responses.GET, "http://my.fog.com/fog/host", json=payload)
        result = self.action.getHostNumber("host4")
        self.assertEqual(len(responses.calls), 1)
        self.assertGoodHeader(responses.calls[0].request)
        self.assertEqual(result, 4)
