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
from actions.actions import detect_hardware_tasks
import json


class DetectHWTestCase(BaseActionTestCase):
    action_cls = detect_hardware_tasks.DetectHardwareTasksAction

    def setUp(self):
        super(DetectHWTestCase, self).setUp()
        self.action = self.get_action_instance()
        job_data = {
            "hardware": {
                "task1": {
                    "power": "on",
                    "image": 1,
                    "hostname": "host1"
                }
            }
        }
        self.action.action_service.set_value("job_1", json.dumps(job_data), local=False)

    def test_detect_hardware_tasks(self):
        result = self.action.run(job_id=1, task_id="task1")
        self.assertTrue(result['power'])
        self.assertTrue(result['hostname'])
        self.assertTrue(result['image'])
