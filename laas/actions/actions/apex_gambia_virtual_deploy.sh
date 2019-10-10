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

SCENARIO="$1"

function install_packages {
    yum -y update
    yum -y groupinstall "Virtualization Host"

    systemctl start libvirtd
    systemctl enable libvirtd

    #special repos and stuff
    yum -y install https://repos.fedorapeople.org/repos/openstack/openstack-queens/rdo-release-queens-1.noarch.rpm
    yum -y install epel-release
    curl -o /etc/yum.repos.d/opnfv-apex.repo http://artifacts.opnfv.org/apex/gambia/opnfv-apex.repo

    yum -y update # synch up repos
    
    #download special package

    wget https://artifacts.opnfv.org/apex/gambia/opnfv-apex-python34-7.1.noarch.rpm -O /root/opnfv-apex-python34.rpm

    yum -y install /root/opnfv-apex-python34.rpm
}


function main {
    install_packages

    #configure??

    opnfv-deploy -v -n /etc/opnfv-apex/network_settings.yaml -d "/etc/opnfv-apex/$SCENARIO.yaml"
}

if ! main &> /root/opnfv-deploy.log; then
    tail -25 /root/opnfv-deploy.log
    opnfv-clean
    exit 1
fi
