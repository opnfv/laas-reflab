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
from lib.fog import FogAction


class SnapshotTask(FogAction):

    def run(self, snapshot_data=None):
        image_id = None
        if "image" in snapshot_data:
            image_id = snapshot_data['image']
        else:
            image_id = self.createSnapshot(snapshot_data)

        host_id = snapshot_data['host']
        return_value = {"host": host_id, "snapshot_id": image_id}
        return return_value

    def createSnapshot(self, data):
        template = {
            'imageTypeID': "3",
            'imagePartitionTypeID': "1",
            'name': "snapshot_",  # TODO: huh?
            'toReplicate': "1",
            'isEnabled': "1",
            'compress': "6",
            'storagegroups': [1],
            'osID': "50"
        }

        response = self.createImage(template)
        image_id = response['id']
        return image_id
