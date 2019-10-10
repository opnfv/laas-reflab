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


class StartImagingAction(FogAction):

    def run(self, host=None):
        """
        Schedules an imaging task for the given host.
        This automatically uses the "associated" disk image.
        """
        host = self.getFogHost(host)
        host_num = str(self.getHostNumber(host))
        url = self.baseURL + 'host/' + host_num + '/task'
        try:
            self.start_imaging(url)
        except Exception:
            self.delTask(host_num)
            self.start_imaging(url)

    def start_imaging(self, url):
        return self.request(url, data={"taskTypeID": 1}, method="post")
