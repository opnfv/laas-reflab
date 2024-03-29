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

from lib.fog import FogAction


class WaitForImagingAction(FogAction):
    def __init__(self, config=None):  # why?
        super(WaitForImagingAction, self).__init__(config=config)

    def run(self, host):
        """
        tracks the imaging task to completion.
        """
        host = self.getFogHost(host)
        imageTaskID = self.getImagingTaskID(host)
        if(imageTaskID < 0):
            print("Failed to find image task to wait on!")
            return
        self.waitForTask(imageTaskID)

    def getImagingTaskID(self, host):
        """
        Sorts through all current tasks to find the image task
        associated with the  given host.
        """
        for task in self.getAllTasks():
            hostname = str(task['host']['name'])
            if hostname == host and int(task['typeID']) == 1:
                return task['id']
        return -1
