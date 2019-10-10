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
from st2tests.base import BaseSensorTestCase
import laas
import responses
import json


class LaaSSensorTest(BaseSensorTestCase):
    sensor_cls = laas.LaaS_Sensor

    def setUp(self):
        super(LaaSSensorTest, self).setUp()
        self.sensor = self.get_sensor_instance(config={
            "dashboard": {
                "address": "http://my.dashboard.com",
                "lab_name": "my_lab"
            }
        })
        self.jobs_url = "http://my.dashboard.com/api/labs/my_lab/jobs/new"
        self.sensor.sensor_service.set_value("jobs", "[]", local=False)
        self.sensor.sensor_service.set_value("lab_auth_token", "my_auth_token", local=False)
        self.sensor.setup()

    def clean(self, sensor):
        # Removes all existing bookings from the keystore
        kvps = sensor.sensor_service.list_values(local=False, prefix="job_")
        for kvp in kvps:
            sensor.sensor_service.delete_value(local=False, name=kvp.name)

    def get_job(self, job_id):
        return {
            "id": job_id,
            "payload": {
                "hardware": "stuff",
                "network": "stuff",
                "access": "stuff",
            }
        }

    def assertJobCreated(self, job_id):
        self.assertTriggerDispatched(
            trigger="laas.start_job_trigger",
            payload={"job_id": job_id}
        )
        self.assertTrue(json.loads(
            self.sensor.sensor_service.get_value("job_" + str(job_id), local=False)
        ))
        # TODO: solve concurrency issues in job stop / start
        # started_jobs = json.loads(self.sensor.sensor_service.get_value("jobs", local=False))
        # self.assertTrue(job_id in started_jobs)

    # Testing Methods

    @responses.activate
    def test_empty_throws_no_triggers(self):
        responses.add(responses.GET, self.jobs_url, json=[])
        self.sensor.poll()
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], 'my_auth_token')
        self.assertEqual(self.get_dispatched_triggers(), [])

    @responses.activate
    def test_new_job_throws_trigger(self):
        responses.add(responses.GET, self.jobs_url, json=[self.get_job(1)])
        self.sensor.poll()
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], 'my_auth_token')
        self.assertJobCreated(1)

    @responses.activate
    def test_job_not_restarted(self):
        self.sensor.sensor_service.set_value("jobs", "[1]", local=False)
        responses.add(responses.GET, self.jobs_url, json=[self.get_job(1)])
        self.sensor.poll()
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], 'my_auth_token')
        self.assertEqual(self.get_dispatched_triggers(), [])

    @responses.activate
    def test_sensor_does_not_die(self):
        # no endpoint added to responses - will throw an error to the sensor
        self.sensor.poll()  # shouldn't throw, should still work next time
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], 'my_auth_token')

        responses.add(responses.GET, self.jobs_url, json=[self.get_job(1)])
        self.sensor.poll()
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.headers['auth-token'], 'my_auth_token')
        self.assertJobCreated(1)

    @responses.activate
    def test_multiple_jobs_started(self):
        responses.add(responses.GET, self.jobs_url, json=[
            self.get_job(1),
            self.get_job(2),
            self.get_job(3)
        ])
        self.sensor.poll()
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['auth-token'], 'my_auth_token')
        self.assertJobCreated(1)
        self.assertJobCreated(2)
        self.assertJobCreated(3)
