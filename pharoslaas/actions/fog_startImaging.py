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
import requests
import sys


class StartImagingAction(FogAction):
    def __init__(self, config=None):
        super(StartImagingAction, self).__init__(config=config)

    def run(self, host=None):
        """
        Schedules an imaging task for the given host.
        This automatically uses the "associated" disk image.
        """
        host = self.getFogHost(host)
        num = str(self.getHostNumber(host))
        url = self.baseURL+'host/'+num+'/task'
        try:
            req = requests.post(
                    url,
                    headers=self.header,
                    json={"taskTypeID": 1}
                    )
            if req.status_code == 200:
                # self.logger.info("%s", "Scheduled image task for host")
                pass
        except Exception:
            # self.logger.warning("%s", "Failed to schedule host imaging")
            # self.logger.warning("%s", "Trying to delete existing image task")
            self.delTask(num)
            req = requests.post(
                    url,
                    headers=self.header,
                    json={"taskTypeID": 1}
                    )
            if req.status_code == 200:
                # self.logger.info("%s", "Scheduled image task for host")
                pass
        sys.exit(0)
