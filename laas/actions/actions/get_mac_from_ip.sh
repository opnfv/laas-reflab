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

TARGET="$1"
GATEWAY="$2"
USER="$3"
COL="\$5"  # string literal '$5' for awk print

if [ -z "$GATEWAY" ]; then
    ping -c 1 "$TARGET" &> /dev/null && ip n | awk "/$TARGET/ {print $COL}" || echo 'unknown'
fi
ssh -o stricthostkeychecking=no -o userknownhostsfile=/dev/null "$USER@$GATEWAY" sh -c "ping -c 1 $TARGET &> /dev/null && ip n | awk '/$TARGET/ {print $5}' || echo 'unknown'"
