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


function detect_os {
    [ -d /etc/netplan ] && echo "ubuntu18" && return 0
    [ -f /etc/network/interfaces ] && echo "ubuntu16" && return 0
    [ -d /etc/sysconfig/network ] && echo "suse" && return 0
    [ -d /etc/sysconfig/network-scripts ] && echo "centos" && return 0
}

function os_specific_map {
    echo "mapping for $1"
    case "$1" in
        ubuntu16)
            echo "do stuff to /etc/network/interfaces"
            FILE="/etc/network/interfaces.d/$2.$3"
            echo "auto $2.$3" > "$FILE"
            echo "iface $2.$3 inet manual" >> "$FILE"
            echo "    vlan-raw-device $2" >> "$FILE"
            ;;
        ubuntu18)
            echo "do stuff to $FILE"
            grep -q "vlans:" "$FILE" || echo "  vlans:" >> "$FILE"
            echo "    vlan$3:" >> "$FILE"
            echo "      id: $3" >> "$FILE"
            echo "      link: $2" >> "$FILE"
            INTERFACES="$INTERFACES $2"
            ;;
        suse)
            echo "do /etc/sysconfig/network stuff"
            FILE="/etc/sysconfig/network/ifcfg-$2.$3"
            echo "ETHERDEVICE=$2" >> "$FILE"
            echo "BOOTPROTO=none" >> "$FILE"
            echo "STARTMODE=auto" >> "$FILE"
            echo "VLAN_ID=$3" >> "$FILE"
            echo "DEFROUTE=no" >> "$FILE"
            ;;
        centos)
            echo "do /etc/sysconfig/network-scripts stuff"
            FILE="/etc/sysconfig/network-scripts/ifcfg-$2.$3"
            echo "TYPE=Vlan" > "$FILE"
            echo "PHYSDEV=$2" >> "$FILE"
            echo "BOOTPROTO=none" >> "$FILE"
            echo "ONBOOT=yes" >> "$FILE"
            echo "VLAN=yes" >> "$FILE"
            echo "VLAN_ID=$3" >> "$FILE"
            echo "DEVICE=$2.$3" >> "$FILE"
            echo "DEFROUTE=no" >> "$FILE"
            echo "IPV4_FAILURE_FATAL=no" >> "$FILE"
            ;;
    esac
}

function translate_interface {
    mac=$(echo "$1" | awk  -F "." '{print $1}')
    vlan=$(echo "$1" | awk  -F "." '{print $2}')
    ifname=$(ip link show | grep -B1 "$mac" | awk -F ': ' 'NR==1{print $2}')
    [ -z "$vlan" ] && echo "$ifname" || echo "$ifname.$vlan"
}

function map {
    mac=$(echo "$1" | awk  -F "-" '{print $1}')
    vlan=$(echo "$1" | awk  -F "-" '{print $2}')
    ifname=$(ip link show | grep -B1 "$mac" | awk -F ': ' 'NR==1{print $2}')
    os=$(detect_os)
    os_specific_map "$os" "$ifname" "$vlan" 
}

function make_default {
    # TODO: check if iface name is actually a mac, and convert
    os=$(detect_os)
    case "$os" in
        ubuntu16)
            echo "do stuff to default in /etc/network/interfaces"
            default="ens4f0"
            mv "/etc/network/interfaces.d/1-$default" "/etc/network/interfaces.d/$default"
            mv "/etc/network/interfaces.d/$1" "/etc/network/interfaces.d/1-$1"
            #use dhcp on default interface
            sed -i 's/dhcp/manual/' /etc/network/interfaces.d/*
            sed -i 's/manual/dhcp/' "/etc/network/interfaces.d/1-$1"
            ;;
        ubuntu18)
            echo "default and others in $FILE"
            echo -e "  ethernets:\n    $1:\n      dhcp4: yes" >> "$FILE"
            for interface in $INTERFACES; do
                [ "$interface" = "$1" ] && continue
                echo -e "    $interface:\n      dhcp4: no" >> "$FILE"
            done
            ;;
        suse)
            echo "do default /etc/sysconfig/network stuff"
            sed -i "s/DEFROUTE='yes'/DEFROUTE='no'/" /etc/sysconfig/network/ifcfg-*
            sed -i "s/DEFROUTE='no'/DEFROUTE='yes'/" "/etc/sysconfig/network/ifcfg-$1"
            sed -i "s/DHCLIENT_SET_DEFAULT_ROUTE='yes'/DHCLIENT_SET_DEFAULT_ROUTE='no'/" /etc/sysconfig/network/ifcfg-*
            sed -i "s/DHCLIENT_SET_DEFAULT_ROUTE='no'/DHCLIENT_SET_DEFAULT_ROUTE='yes'/" "/etc/sysconfig/network/ifcfg-$1"
            sed -i "s/BOOTPROTO='dhcp'/BOOTPROTO='none'/" /etc/sysconfig/network/ifcfg-*
            sed -i "s/BOOTPROTO='none'/BOOTPROTO='dhcp'/" "/etc/sysconfig/network/ifcfg-$1"
            ;;
        centos)
            echo "do default /etc/sysconfig stuff"
            sed -i 's/DEFROUTE=yes/DEFROUTE=no/' /etc/sysconfig/network-scripts/ifcfg-*
            sed -i 's/DEFROUTE=no/DEFROUTE=yes/' "/etc/sysconfig/network-scripts/ifcfg-$1"
            sed -i 's/BOOTPROTO=dhcp/BOOTPROTO=none/' /etc/sysconfig/network-scripts/ifcfg-*
            sed -i 's/BOOTPROTO=none/BOOTPROTO=dhcp/' "/etc/sysconfig/network-scripts/ifcfg-$1"
            ;;
    esac
}


#main
if [ "$(detect_os)" = "ubuntu18" ]; then
    FILE="/etc/netplan/config.yaml"
    INTERFACES=""
    echo -e "network:\n  version: 2\n  renderer: networkd" > $FILE
fi

for mapping in $(echo "$1" | tr '+' '\n'); do
    echo "mapping $mapping"
    map "$mapping"
done

DEFAULT=$(translate_interface "$2")

echo "setting default $DEFAULT"
make_default "$DEFAULT"
