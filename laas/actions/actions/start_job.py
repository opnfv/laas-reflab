##############################################################################
# Copyright 2018 Parker Berberian and Others                                 #
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
from st2actions.runners.pythonrunner import Action
import json


class StartJobAction(Action):

    def run(self, job_id=None):
        jobs = set(json.loads(self.action_service.get_value("jobs", local=False)))
        if job_id in jobs:
            print("job already started!")
        jobs.add(job_id)
        self.action_service.set_value("jobs", json.dumps(list(jobs)), local=False)
