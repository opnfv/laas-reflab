#!/bin/bash
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

# clone git repo
git clone https://git.opnfv.org/fuel
cd fuel || exit 1
git checkout stable/gambia

export TERM="xterm-256color"

#write out config files
mkdir -p /home/fuel/config/labs/LaaS
mkdir /home/fuel/tmpdir
chmod -R 777 /home/fuel
echo "$1" > /home/fuel/config/labs/LaaS/pod1.yaml
echo "$2" > /home/fuel/config/labs/LaaS/idf-pod1.yaml
echo "$2" > /root/LaaS/idf-pod.yaml

# deploy command
ci/deploy.sh \
    -l LaaS \
    -p pod1 \
    -b file:///home/fuel/config \
    -s os-nosdn-nofeature-noha \
    -S /home/fuel/tmpdir \
    -D |& tee /home/opnfv/fuel_deploy.log
