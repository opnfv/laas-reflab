#!/bin/bash
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


KEY="$1"
HOSTS="$2"
echo "$KEY" > tmpkey.pub

RET=0

for HOST in $(echo "$HOSTS" | tr ',' '\n'); do
    ssh-copy-id -f -i tmpkey.pub -o userknownhostsfile=/dev/null -o stricthostkeychecking=no opnfv@"$HOST" || RET=1
done
rm -f tmpkey.pub

exit $RET
