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

ctlprivip=$(virsh domifaddr ctl01 | grep 10.20.0 | awk '{print $4}' | cut -d "/" -f 1)
ctlpubip=$(ssh -i fuel/mcp/scripts/mcp.rsa ubuntu@"$ctlprivip" ip r | grep 10.16.0.0/24 | awk '{print $9}')
#default is 10.16.0.101?
MYIP=$1
DESTINATION=$ctlpubip
MYBRIDGE=10.16.0.1
DESTNETWORK=10.16.0.0/24
PORT=8078

iptables -I INPUT 2 -d "$MYIP" -p tcp --dport "$PORT" -j ACCEPT
iptables -t nat -I INPUT 1 -d "$MYIP" -p tcp --dport "$PORT" -j ACCEPT
iptables -I FORWARD -p tcp --dport "$PORT" -j ACCEPT

iptables -t nat -I PREROUTING -p tcp -d "$MYIP" --dport "$PORT" -j DNAT --to-destination "$DESTINATION:$PORT"
iptables -t nat -I POSTROUTING -p tcp -s "$DESTINATION" ! -d "$DESTNETWORK" -j SNAT --to-source "$MYIP"

iptables -t nat -I POSTROUTING 2 -d "$DESTINATION" -j SNAT --to-source "$MYBRIDGE"
