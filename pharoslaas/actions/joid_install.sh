#!/bin/bash
#############################################################################
#Copyright 2017 Parker Berberian and others                                 #
#                                                                           #
#Licensed under the Apache License, Version 2.0 (the "License");            #
#you may not use this file except in compliance with the License.           #
#You may obtain a copy of the License at                                    #
#                                                                           #
#    http://www.apache.org/licenses/LICENSE-2.0                             #
#                                                                           #
#Unless required by applicable law or agreed to in writing, software        #
#distributed under the License is distributed on an "AS IS" BASIS,          #
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
#See the License for the specific language governing permissions and        #
#limitations under the License.                                             #
#############################################################################

if [ "$1" ]; then
    # parses the passed scenario
    args=($(echo "$1" | tr "-" "\n"))
    # args is array: [os, nosdn, nofeature, noha]
else
    args=('os' 'nosdn' 'nofeature' 'noha')
fi
# the deploy script expects 'none' rather than 'nofeature'
if [ "nofeature" == "${args[2]}" ]; then
    args[2]="none"
fi
if [ "os" == "${args[0]}" ]; then
    args[0]="openstack"
fi
# grabs the joid repo
git clone "https://gerrit.opnfv.org/gerrit/joid.git"
# working directory has to be where 03-maasdeploy is
cd joid/ci || exit 1
# virtualy deploy maas
./03-maasdeploy.sh virtual
# deploys OPNFV with the given scenario
./deploy.sh -o newton -s "${args[1]}" -t "${args[3]}" -l default -d xenial -m "${args[0]}" -f "${args[2]}"

juju gui --show-credentials --no-browser &>output.juju

DESTINATION=$( grep -E -o "[0-9].*[0-9]" output.juju | tr -d '/' | sed s/:.*//g )
MYIP=$( ip a | grep -E -o "10.10.30.[0-9]+" | sed s/^.*255.*$//g | tr -d '\n' )

rm -f output.juju


############## Uses NAT to make juju gui available at my public address ####################

MYIP=$1
DESTINATION=$2
MYBRIDGE=192.168.122.1
DESTNETWORK=192.168.122.0/24
PORT=17070

iptables -I INPUT 2 -d "$MYIP" -p tcp --dport "$PORT" -j ACCEPT
iptables -t nat -I INPUT 1 -d "$MYIP" -p tcp --dport "$PORT" -j ACCEPT
iptables -I FORWARD -p tcp --dport "$PORT" -j ACCEPT

iptables -t nat -I PREROUTING -p tcp -d "$MYIP" --dport "$PORT" -j DNAT --to-destination "$DESTINATION:$PORT"
iptables -t nat -I POSTROUTING -p tcp -s "$DESTINATION" ! -d "$DESTNETWORK" -j SNAT --to-source "$MYIP"

iptables -t nat -I POSTROUTING 2 -d "$DESTINATION" -j SNAT --to-source "$MYBRIDGE"
