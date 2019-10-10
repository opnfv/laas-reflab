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


#this script will deploy a virtual POD using Fuel gambia

#this script assumes:
#   /home/fuel/config exists and has the configuration files for virtual1
#   /home/fuel/tmpdir exists
#   /home/fuel/* permissions are correct

SCENARIO="$1"
VERSION="$2"


function install_packages {
    if grep -iq centos /etc/os-release; then #centos
        yum -y update
        yum -y install epel-release git
        yum -y groupinstall "Virtualization Host"
        systemctl start libvirtd
        systemctl enable libvirtd
    elif grep -iq ubuntu /etc/os-release; then #ubuntu
        apt update
        apt -y upgrade
        apt -y install libvirt-bin git
        #apt should do this for us, but lets be double safe
        systemctl start libvirtd
        systemctl enable libvirtd
    fi
}

function install_fuel {
    git clone https://git.opnfv.org/fuel
    cd fuel || exit 1
    if ! git checkout "$VERSION"; then
        echo "failed to checkout $VERSION, defaulting to opnfv-7.1.0"
        git checkout opnfv-7.1.0
    fi
    chmod -R 777 /home/fuel/
}


function main {
    install_packages

    install_fuel

    ci/deploy.sh -l IOL -p virtual1 -b file:///home/fuel/config -s "$SCENARIO" -D -S /home/fuel/tmpdir
}


# hack for tput
export TERM=xterm-256color
main &> /root/opnfv-deploy.log
