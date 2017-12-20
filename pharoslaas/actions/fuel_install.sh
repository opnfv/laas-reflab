#!/bin/bash
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

git clone https://git.opnfv.org/fuel

export TERM='xterm-256color' # hack to avoid tput error

#make idf and pdf virtual
mv fuel/mcp/config/labs/local/pod1.yaml fuel/mcp/config/labs/local/virtual_pod1.yaml
mv fuel/mcp/config/labs/local/idf-pod1.yaml fuel/mcp/config/labs/local/idf-virtual_pod1.yaml

fuel/ci/deploy.sh -b file://"$(pwd)"/fuel/mcp/config -l local -p virtual_pod1 -s os-nosdn-nofeature-noha
