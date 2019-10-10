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
import requests
import json
from st2reactor.sensor.base import PollingSensor


class LaaS_Sensor(PollingSensor):

    def setup(self):
        self.logger = self.sensor_service.get_logger(name=self.__class__.__name__)
        self.auth_token = self.sensor_service.get_value(name="lab_auth_token", local=False)
        self.logger.info("got auth token %s", self.auth_token)

    def poll(self):
        try:
            jobs = json.loads(self.sensor_service.get_value("jobs", local=False))
            dashboard = self._config['dashboard']['address']
            name = self._config['dashboard']['lab_name']
            url = dashboard + "/api/labs/" + name + "/jobs/new"
            self.logger.info("polling at url %s", url)
            header = {"auth-token": self.auth_token}
            todo_jobs = requests.get(url, timeout=10, headers=header).json()
            for job_data in todo_jobs:
                if job_data['id'] in jobs:
                    continue
                self.logger.info("doing job %s", str(job_data['id']))
                # put job into datastore for workflow
                self.sensor_service.set_value(
                    "job_" + str(job_data['id']),
                    json.dumps(job_data['payload']),
                    local=False
                )
                # dispatch trigger
                self.sensor_service.dispatch(
                    trigger="laas.start_job_trigger",
                    payload={"job_id": job_data['id']}
                )
        except Exception as e:
            self.logger.exception("Failed to poll(): %s", str(e))

    # Sensor Interface Methods #

    def cleanup(self):
        # called when st2 goes down
        pass

    def add_trigger(self, trigger):
        # called when trigger is created
        pass

    def update_trigger(self, trigger):
        # called when trigger is updated
        pass

    def remove_trigger(self, trigger):
        # called when trigger is deleted
        pass
