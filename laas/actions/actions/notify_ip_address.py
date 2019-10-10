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


class NotifyIPAction(NotifyAction):
    template = """
    Your host may be reached at any
    of the following ip addresses:
    {{info.address}}

    {% if info.hostname %}
    You may also use the following hostname:
    {{info.hostname}}
    {% endif %}
    """

    def run(self, addresses=None, hostname=None, job_id=None, task_id=None):
        info = {
            "address": addresses,
            "hostname": hostname
        }
        self.notify(self.template, info, job_id, task_id)
