##############################################################################
# Copyright 2019 Sawyer Bergeron and Others                                  #
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


class FogGetTargetImageAction(FogAction):
    def __init__(self, config=None):
        super(FogGetTargetImageAction, self).__init__(config=config)

    def run(self, host="None", from_image="None", from_os="None", target_image="None", target_os="None"):
        existing_target = self.getImageID(target_image, target_os, host)

        existing_source = self.getImageID(from_image, from_os, host)

        if existing_source == -1:
            raise Exception("Invalid source args, source image not found")

        # we found a matching, existing, target image
        if existing_target != -1:
            return existing_target

        # handle being given just one operand image, it is both source and target
        if target_image == "None" and target_os == "None":
            return existing_source

        if target_image == "None":
            raise ValueError("GetTargetImage requires a target image if the provided target OS doesn't exist")

        # if we're here, we have valid source and need to create a new target
        return self.deriveImage(existing_source, target_image).json()['id']
