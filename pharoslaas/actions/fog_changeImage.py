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


class ChangeImageAction(FogAction):
    def __init__(self, config):
        super(ChangeImageAction, self).__init__(config=config)

    def run(self, host=None, image=None, os=None):
        """
        Sets the image to be used during ghosting to the image
        with id imgNum. host can either be a hostname or number.
        """
        imgNum = self.getImageID(img=image, os=os, host=host)
        if imgNum < 0:
            return
        host = self.getFogHost(host)
        hostnum = self.getHostNumber(host)
        url = self.baseURL+"host/"+str(hostnum)
        host_conf = requests.get(url, headers=self.header).json()
        host_conf['imageID'] = str(imgNum)
        requests.put(url+"/edit", headers=self.header, json=host_conf)
