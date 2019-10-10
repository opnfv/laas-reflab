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


if ! STATUS=$(ipmitool -I lanplus -H "$1" -U "$2" -P "$3" chassis power status); then
    sleep 45
    if ! STATUS=$(ipmitool -I lanplus -H "$1" -U "$2" -P "$3" chassis power status); then
        exit 1
    fi
fi

ONOFF=$(echo "$STATUS" | cut -d ' ' -f 4)

if [ "$ONOFF" == "off" ]; then
    case "$4" in
        "cycle")
            ipmitool -I lanplus -H "$1" -U "$2" -P "$3" chassis power on
            exit $?
            ;;
        "off")
            exit 0
            ;;
    esac
else # Server is on
    case "$4" in
        "on")
            ipmitool -I lanplus -H "$1" -U "$2" -P "$3" chassis power cycle
            exit $?
            ;;
    esac
fi

ipmitool -I lanplus -H "$1" -U "$2" -P "$3" chassis power "$4"