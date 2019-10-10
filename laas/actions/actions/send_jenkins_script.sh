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
destination="$1"
hostname="$2"
secret="$3"
script="$4"

cp "$script" ./tmpscript

sed -i "s/HOSTNAME_REPLACE/$hostname/" tmpscript
sed -i "s/SECRET_REPLACE/$secret/" tmpscript

scp -o userknownhostsfile=/dev/null -o stricthostkeychecking=no tmpscript root@"$destination":/root/jenkins_connect.sh
rm tmpscript
