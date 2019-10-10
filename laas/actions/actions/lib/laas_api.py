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

from st2actions.runners.pythonrunner import Action
import jinja2
import requests


class DashboardAction(Action):

    def __init__(self, *args, **kwargs):
        self._config = kwargs.get('config', None)
        super(DashboardAction, self).__init__(*args, **kwargs)
        server = self._config['dashboard']['address']
        name = self._config['dashboard']['lab_name']
        self.base_url = server + "/api/labs/" + name
        self.header = {"auth-token": self.action_service.get_value("lab_auth_token", local=False)}

    def send_api_message(self, endpoint="", payload={}):
        url = self.base_url + endpoint
        r = requests.post(url, data=payload, timeout=10, headers=self.header)
        print("response " + str(r.status_code))
        return r


class TaskStatusAction(DashboardAction):

    def set_status(self, job_id=None, task_id=None, lab_token=None, status=0):
        payload = {"status": status}
        if lab_token:
            payload['lab_token'] = lab_token

        return self.send_api_message(
            endpoint="/jobs/" + str(job_id) + "/" + str(task_id),
            payload=payload
        )


class NotifyAction(DashboardAction):

    def notify(self, template, info, job_id, task_id, lab_token=None):
        message = self.render(template, info)
        print(message)
        self.send_notification(
            job_id=job_id,
            task_id=task_id,
            message=message,
            lab_token=lab_token
        )

    def render(self, template, info):
        jinja_template = jinja2.Template(template)
        return jinja_template.render(info=info)

    def send_notification(self, job_id=None, task_id=None, message="", lab_token=None):
        endpoint = "/jobs/" + str(job_id) + "/" + task_id
        payload = {"message": message}
        if lab_token:
            payload['lab_token'] = lab_token
        self.send_api_message(endpoint, payload=payload)
