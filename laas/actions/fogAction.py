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

import requests
import sys
import json
import time
from st2actions.runners.pythonrunner import Action


class FogAction(Action):
    """
    This class talks with the REST web api for the FOG server.
    """
    def __init__(self, config=None):
        self.baseURL = config['fog']['address']
        self.fogKey = config['fog']['api_key']
        self.userKey = config['fog']['user_key']
        self.updateHeader()

    def updateHeader(self):
        """
        recreates the http header used to talk to the fog api
        """
        self.header = {}
        self.header['fog-api-token'] = self.fogKey
        self.header['fog-user-token'] = self.userKey

    def getImageID(self, img=None, os=None, host=None):
        """
        returns the numerical id associated with the given img name or
        operating system. If both are given, the img gets priority.
        if img is a number, it is assumed to be a valid id
        """
        # st2 will promote an empty arg to the str "None" :(
        if not img or img == "None":
            return self.getImageIDFromOS(os, host)
        try:
            return int(img)
        except:
            url = self.baseURL+"image"
            images = requests.get(url=url, headers=self.header)
            images = images.json()['images']
            for image in images:
                if img == image['name']:
                    return image['id']
        return -1

    def getImageIDFromOS(self, os, host):
        enum = {"ubuntu": "ubuntu_image",
                "centos": "centos_image",
                "suse": "suse_image"
                }
        os = os.lower()
        if os not in enum.keys():
            return -1
        host_dict = json.loads(
                self.action_service.get_value(name=host, local=False)
                )
        return int(host_dict[enum[os]])

    def delTask(self, hostNum):
        """
        Tries to delete an existing task for the host
        with hostNum as a host number
        """
        try:
            url = self.baseURL+'fog/host/'+str(hostNum)+'/cancel'
            req = requests.delete(url, headers=self.header)
            if req.status_code == 200:
                self.logger.info("%s", "successfully deleted image task")
        except Exception:
            self.logger.exception("Failed to delete the imaging task!")

    def getHostNumber(self, hostname):
        """
        returns the host number of given host
        """
        try:
            req = requests.get(self.baseURL+"host", headers=self.header)
            hostData = req.json()
            if hostData is not None:
                for hostDict in hostData['hosts']:
                    if hostname == hostDict['name']:
                        return hostDict['id']
            return -1
        except Exception:
            self.logger.exception('%s', "Failed to connect to the FOG server")

    def request(self, url, data=None, method="get"):
        if data is not None:
            return self.dataRequest(url, data, method=method)
        try:
            response = requests.get(url, headers=self.header)
            return response.json()
        except Exception:
            self.logger.exception("Failed to reach FOG at %s", url)
            sys.exit(1)

    def dataRequest(self, url, data, method="post"):
        methods = {
                "post": requests.post,
                "put": requests.put
                }
        try:
            return methods[method](url, json=data, headers=self.header)
        except Exception:
            self.logger.exception("Failed to reach FOG at %s", url)
            sys.exit(1)

    def getFogHost(self, host):
        hostData = self.action_service.get_value(host, local=False)
        return json.loads(hostData)['fog_name']

    def waitForTask(self, taskID):
        """
        Watches a task and waits for it to finish (disapear).
        There may be a smarter way to do this and track errors,
        but st2 will timeout for me if something goes wrong
        """
        task = self.getTask(taskID)
        while(task):
            time.sleep(15)
            task = self.getTask(taskID)

    def getAllTasks(self):
        try:
            tasks = requests.get(
                    self.baseURL+'task/current',
                    headers=self.header
                    ).json()['tasks']
            return tasks
        except Exception:
            return []

    def getTask(self, taskID):
        for task in self.getAllTasks():
            if task['id'] == taskID:
                return task
        return {}
