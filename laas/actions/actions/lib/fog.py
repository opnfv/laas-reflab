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
import json
import time
from st2actions.runners.pythonrunner import Action


class FogAction(Action):
    """
    This class talks with the REST web api for the FOG server.
    """
    def __init__(self, config=None):
        super(FogAction, self).__init__(config=config)
        self.baseURL = config['fog']['address']
        self.fogKey = config['fog']['api_key']
        self.userKey = config['fog']['user_key']
        self.updateHeader()

    def updateHeader(self):
        """
        recreates the http header used to talk to the fog api
        """
        self.header = {
            'fog-api-token': self.fogKey,
            'fog-user-token': self.userKey
        }

    def run(self):
        pass  # fake run method to make st2 happy

    def createImage(self, image):
        url = self.baseURL + "image"
        return requests.post(url, data=json.dumps(image), headers=self.header, timeout=10)

    def getImage(self, img=None, os=None, host=None, snapshot=None):
        imgID = self.getImageID(img=img, os=os, host=host, snapshot=snapshot)
        url = self.baseURL + "image/" + str(imgID)
        image = requests.get(url, headers=self.header, timeout=10)
        return image.json()

    def deriveImage(self, from_image="None", to_new_image="None"):
        """
        @param from_image: required, expects a string that is the name of the image to be derived from
        @param to_image: required, expects a string that is the name of the new image we want to create
        @return: request object containing keys related to the image from the fog rest API
        @return: no value, most likely addition (if any) would be to parse the response and return image id
        """
        if from_image == "None" or to_new_image == "None":
            raise ValueError("deriveImage requires defined values for both from_image and to_new_image")

        to_new_image = to_new_image.lower().replace(" ", "_")
        newImage = {}

        from_image = self.getImage(from_image)

        basicKeys = [
            'imagePartitionTypeID',
            'toReplicate',
            'isEnabled',
            'compress',
            'osID',
            'imageTypeID'
        ]
        for key in basicKeys:
            newImage[key] = from_image[key]

        newImage['name'] = to_new_image
        newImage['path'] = to_new_image

        return self.createImage(newImage)

    def getImageID(self, img=None, os=None, host=None, snapshot=None):
        """
        returns the numerical id associated with the given img name or
        operating system. If both are given, the img gets priority.
        if img is a number, it is assumed to be a valid id
        """
        # if img is an int, return it
        try:
            return int(img)
        except:
            pass

        # if given an os, translate to id
        # st2 will promote an empty arg to the str "None" :(
        if os and os != "None":
            return self.getImageIDFromOS(os, host)

        if snapshot and snapshot != "None":
            return self.getImageIDFromSnapshot(snapshot)

        if img and img != "None":
            url = self.baseURL + "image"
            images_api_payload = requests.get(url=url, headers=self.header, timeout=10)
            images = images_api_payload.json()['images']
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
        if os not in enum:
            return -1
        host_dict = json.loads(
            self.action_service.get_value(name=host, local=False)
        )
        return int(host_dict[enum[os]])

    def getImageIDFromSnapshot(self, snapshot):
        try:
            enum = json.loads(
                self.action_service.get_value(
                    name="snapshots",
                    local=False
                )
            )
            return int(enum[snapshot])
        except:
            self.logger.exception("Could not get ID")
            return -1

    def delTask(self, hostNum):
        """
        Tries to delete an existing task for the host
        with hostNum as a host number
        """
        try:
            url = self.baseURL + 'fog/host/' + str(hostNum) + '/cancel'
            req = requests.delete(url, headers=self.header, timeout=10)
            if req.status_code == 200:
                print("successfully deleted image task")
        except Exception:
            self.logger.exception("Failed to delete the imaging task!")

    def getHostNumber(self, hostname):
        """
        returns the host number of given host
        """
        try:
            req = requests.get(self.baseURL + "host", headers=self.header, timeout=10)
            hostData = req.json()
            if hostData is not None:
                for hostDict in hostData['hosts']:
                    if hostname == hostDict['name']:
                        return hostDict['id']
            return -1
        except Exception:
            self.logger.exception("Failed to connect to the FOG server")

    def request(self, url, data=None, method="get"):
        if data is not None:
            if method == "get":
                method = "post"  # ergonomics - if I'm passing in data, I obviously want to do a POST
            return self.dataRequest(url, data, method=method)
        try:
            response = requests.get(url, headers=self.header, timeout=10)
            return response.json()
        except Exception:
            self.logger.exception("Failed to reach FOG at %s", url)

    def dataRequest(self, url, data, method="post"):
        methods = {
            "post": requests.post,
            "put": requests.put
        }
        try:
            return methods[method](url, json=data, headers=self.header, timeout=10)
        except Exception:
            self.logger.exception("Failed to reach FOG at %s", url)

    def getFogHost(self, host):
        hostData = self.action_service.get_value(host, local=False)
        return json.loads(hostData)['fog_name']

    def getFogHostData(self, host):
        hostID = self.getHostNumber(host)
        url = self.baseURL + "host/" + str(hostID)
        resp = requests.get(url, headers=self.header, timeout=10)
        return resp.json()

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
                self.baseURL + 'task/current',
                headers=self.header,
                timeout=10
            ).json()['tasks']
            return tasks
        except Exception:
            self.logger.exception("failed to get tasks")
            return []

    def getTask(self, taskID):
        for task in self.getAllTasks():
            if task['id'] == taskID:
                return task
        return {}
