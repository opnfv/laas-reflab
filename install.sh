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

#installs deps 
if which apt ; then
    apt update && apt -y upgrade
    apt -y install libvirt-dev curl gcc libsas12-dev python-dev libldap2-dev libssl-dev
elif which yum ; then
    yum -y update
    yum -y install curl libvirt-devel gcc python-devel openldap-devel
else
    echo "Can only run on ubuntu or centos. exiting"
    exit 1
fi
#run their install script
curl -sSL https://stackstorm.com/packages/install.sh | bash -s -- --user=st2admin --password='admin'
#change ssh user to root
sed -i 's/user = stanley/user = root/' /etc/st2/st2.conf
sed -i 's/ssh_key_file = \/home\/stanley\/.ssh\/stanley_rsa/ssh_key_file = \/root\/.ssh\/id_rsa/' /etc/st2/st2.conf

mv pharoslab/ /opt/stackstorm/packs/
cp /opt/stackstorm/packs/pharoslab/pharoslab.yaml.example /opt/stackstorm/configs

echo "stackstorm should now be installed. Please edit /opt/stackstorm/configs/pharoslab.yaml and /opt/stackstorm/packs/pharoslab/hosts.json appropriately and run the setup script"
