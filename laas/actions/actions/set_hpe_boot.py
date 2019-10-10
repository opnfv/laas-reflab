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
from st2actions.runners.pythonrunner import Action


class HPEBootAction(Action):

    ribcl_script = """
    <?xml version="1.0"?>
    <?iol entity-procesing="standard"?>
    <?xmlilo output-format="xml"?>
    <RIBCL VERSION="2.0">
      <LOGIN USER_LOGIN="CHANGEUSER" PASSWORD="CHANGEPASSWORD">
        <SERVER_INFO MODE="write">
          <SET_PERSISTENT_BOOT>
            <DEVICE value="Boot000E"/>
          </SET_PERSISTENT_BOOT>
        </SERVER_INFO>
      </LOGIN>
    </RIBCL>
    """

    def run(self, host=None, passwd=None, user=None):
        self.ribcl_script = self.ribcl_script.replace("CHANGEUSER", user)
        self.ribcl_script = self.ribcl_script.replace("CHANGEPASSWORD", passwd)
        url = "http://" + host + "/ribcl"
        response = requests.post(url, data=self.ribcl_script, verify=False)

        print("Sent script to set boot order to host " + host)
        print("Got response code " + str(response.status_code))
