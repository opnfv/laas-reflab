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

ADMIN_USER="$1"
ADMIN_PASS="$2"
HOST="$3"
USERID="$4"

USER_PASS=$(st2 key get "$5" --decrypt --attr value --json | tr -d "[:punct:]" | grep  value | awk '{print $2}')

if [ -z "$USER_PASS" ]; then
    echo "Failed to read password from keystore!"
    exit 1
fi

function set_pass {
    ipmitool -I lanplus -U "$ADMIN_USER" -P "$ADMIN_PASS" -H "$HOST" user set password "$USERID" "$USER_PASS"
}

if ! set_pass; then
    sleep 30
    set_pass
fi
