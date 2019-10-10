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

from lib.laas_api import NotifyAction


class NotifySSHAction(NotifyAction):
    template = """
    Your ssh keys have been copied to your host(s). You may connect with the following:
        {% for host in info.hosts %}
        ssh {{info.user}}@{{host}}
        {% endfor %}
    """

    def run(self, user=None, hosts=None, job_id=None, task_id=None):
        info = {
            "user": user,
            "hosts": hosts
        }
        self.notify(self.template, info, job_id, task_id)
