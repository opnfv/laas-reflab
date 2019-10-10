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

import requests
import json


class NXCommand(object):

    TYPE_SHOW = "cli_show"
    TYPE_CONFIG = "cli_config"

    def __init__(self, switch, auth):
        self.url = "http://" + switch + "/ins"
        self.version = "1.0"
        self.type = "cli_conf"
        self.chunk = "0"
        self.sid = "1"
        self.output_format = "json"
        self.input = []

        self.user = auth['user']
        self.password = auth['password']

    def add_command(self, cmd):
        self.input.append(cmd)

    def execute(self):
        resp = requests.post(
            self.url,
            data=json.dumps(self.serialize()),
            timeout=10,
            headers={"content-type": "text/json"},
            auth=(self.user, self.password)
        )
        try:
            return resp.json()
        except:
            return resp.text

    def serialize(self):
        return {
            "ins_api": {
                "version": self.version,
                "type": self.type,
                "chunk": self.chunk,
                "sid": self.sid,
                "input": " ;".join(self.input),
                "output_format": self.output_format
            }
        }
