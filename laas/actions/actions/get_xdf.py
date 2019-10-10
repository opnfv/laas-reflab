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
import requests


class XDF_Action(Action):
    def __init__(self, *args, **kwargs):
        self._config = kwargs.get('config', None)
        super(XDF_Action, self).__init__(*args, **kwargs)

    def run(self, task_data={}):
        server = self._config['dashboard']['address']
        pdf_endpoint = task_data['opnfv']['pdf']
        idf_endpoint = task_data['opnfv']['idf']
        header = {"auth-token": self.action_service.get_value("lab_auth_token", local=False)}
        pdf = requests.get(server + pdf_endpoint, timeout=10, headers=header)
        idf = requests.get(server + idf_endpoint, timeout=10, headers=header)
        return {"pdf": pdf.text, "idf": idf.text}
