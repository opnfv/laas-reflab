##############################################################################
# Copyright 2017 Parker Berberian and Others                                 #
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

from fogAction import FogAction
import sys


class waitForCaptureAction(FogAction):
    def __init__(self, config=None):
        super(waitForCaptureAction, self).__init__(config=config)

    def run(self, host=None):
        host = self.getFogHost(host)
        captureTaskID = self.getCaptureTaskID(host)
        if(captureTaskID < 0):
            sys.exit(1)
        self.waitForTask(captureTaskID)

    def getCaptureTaskID(self, host=None):
        for task in self.getAllTasks():
            hostname = str(task['host']['name'])
            if hostname == host and int(task['typeID']) == 2:
                return task['id']
            return -1
