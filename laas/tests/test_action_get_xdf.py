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
from actions.actions import get_xdf
import responses


class GetXDFTestCase(BaseActionTestCase):
    action_cls = get_xdf.XDF_Action

    def setUp(self):
        super(GetXDFTestCase, self).setUp()
        self.action_service.set_value("lab_auth_token", "my_auth_token", local=False)
        self.action = self.get_action_instance(config={
            "dashboard": {
                "address": "http://my.dashboard.com",
                "lab_name": "my_lab"
            }
        })

    @responses.activate
    def test_xdf_retrieved(self):
        urls = [
            "http://my.dashboard.com/api/some/endpoint/pdf",
            "http://my.dashboard.com/api/some/endpoint/idf"
        ]
        responses.add(responses.GET, urls[0])
        responses.add(responses.GET, urls[1])
        self.action.run(task_data={
            "opnfv": {
                "pdf": "/api/some/endpoint/pdf",
                "idf": "/api/some/endpoint/idf",
            }
        })
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], "my_auth_token")
        self.assertEqual(responses.calls[1].request.headers['auth-token'], "my_auth_token")

        try:
            urls.remove(responses.calls[0].request.url)
            urls.remove(responses.calls[1].request.url)
        except ValueError:
            self.fail("Requests were sent to the wrong URLs")
