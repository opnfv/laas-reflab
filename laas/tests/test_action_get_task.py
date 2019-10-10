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
from actions.actions import get_task
import json


class GetTaskTestCase(BaseActionTestCase):
    action_cls = get_task.GetTaskAction

    def setUp(self):
        super(GetTaskTestCase, self).setUp()
        self.action = self.get_action_instance()

    def test_get_task_multiple_tasks(self):
        self.action.action_service.set_value("job_1", json.dumps({
            "access": {
                "task1": "asdf",
                "task2": "fdsa"
            }
        }), local=False)
        result = self.action.run(job_id=1, type="access", task_id="task1")
        self.assertEqual(result, "asdf")

    def test_get_single_task(self):
        self.action.action_service.set_value("job_1", json.dumps({
            "access": {"task1": "asdf"},
            "hardware": {"task10": "foobar"}
        }), local=False)
        result = self.action.run(job_id=1, type="hardware", task_id="task10")
        self.assertEqual("foobar", result)
