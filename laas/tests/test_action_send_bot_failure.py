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
from actions.actions import send_bot_failure
import responses
import json


class SendBotFailureTestCase(BaseActionTestCase):
    action_cls = send_bot_failure.BotFailureAction

    def setUp(self):
        super(SendBotFailureTestCase, self).setUp()
        self.action_service.set_value("lab_auth_token", "my_auth_token", local=False)
        self.action = self.get_action_instance(config={
            "bot": {
                "endpoints": {
                    "failure": "failure",
                    "notification": "notification"
                },
                "address": "http://my.bot.com/endpoint/"
            }
        })

    @responses.activate
    def test_send_bot_failure(self):
        responses.add(responses.POST, "http://my.bot.com/endpoint/failure")
        payload = {"k1": "v1", "k2": "v2"}
        self.action.run(**payload)
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['Content-Type'], "application/json")
        self.assertEqual(json.dumps(payload), responses.calls[0].request.body)
