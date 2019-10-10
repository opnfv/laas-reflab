#!/bin/bash
##############################################################################
# Copyright 2019 Parker Berberian and Others                                 #
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
    [ -f /etc/network/interfaces ] && echo "ubuntu16" && return 0
    [ -d /etc/sysconfig/network ] && echo "suse" && return 0
    [ -d /etc/sysconfig/network-scripts ] && echo "centos" && return 0
}

function create_bridge {
    os="$1"
    bridge="$2"
    ifname="$3"
    ipaddr="$4"
    case "$os" in
        ubuntu16)
            echo "do stuff to /etc/network/interfaces"
            BRFILE="/etc/network/interfaces.d/$bridge"
            IFFILE="/etc/network/interfaces.d/$ifname"

            #create bridge config
            echo "auto $bridge" >> "$BRFILE"
            if [ "$ipaddr" = "dhcp" ]; then
                echo "iface $bridge inet dhcp" >> "$BRFILE"
            else
                echo "iface $bridge inet manual" >> "$BRFILE"
                echo "address $ipaddr" >> "$BRFILE"
                # network and netmask?
            fi
            echo "bridge_ports $ifname" >> "$BRFILE"
            echo "bridge_stp off" >> "$BRFILE"
            echo "bridge_fd 0" >> "$BRFILE"
            echo "bridge_maxwait 0" >> "$BRFILE"

            #change old interface
            if [ ! -f "$IFFILE" ]; then
                IFFILE="/etc/network/interfaces.d/1-$ifname"
            fi
            rm -f "$IFFILE"
            ;;

        suse)
            echo "not supported"
            ;;
        centos)
            echo "do /etc/sysconfig/network-scripts stuff"
            BRFILE="/etc/sysconfig/network-scripts/ifcfg-$bridge"
            IFFILE="/etc/sysconfig/network-scripts/ifcfg-$ifname"

            #change device config
            sed -i '/DEFROUTE/d' "$IFFILE"
            sed -i '/IPADDR/d' "$IFFILE"
            sed -i '/PREFIX/d' "$IFFILE"
            sed -i 's/BOOTPROTO=dhcp/BOOTPROTO=none/' "$IFFILE"
            echo "BRIDGE=$bridge" >> "$IFFILE"

            #create bridge config
            {
                echo "DEVICE=$bridge"
                echo "TYPE=Bridge"
                echo "ONBOOT=yes"
            } >> "$BRFILE"
            if [ "$ipaddr" = "dhcp" ]; then
                {
                    echo "BOOTPROTO=dhcp"
                    echo "DEFROUTE=yes"
                } >> "$BRFILE"
                # create local script that runs even if we lose SSH
                {
                    echo "ifup $bridge"
                    echo "dhclient -r $ifname"
                    echo "ip a flush $ifname"
                    echo "brctl addif $bridge $ifname"
                    echo "ip l set dev $bridge up"
                    echo "dhclient $bridge"
                } >> /tmp/net.sh
                bash /tmp/net.sh &
            else
                {
                    echo "IPADDR=$ipaddr"
                    echo "PREFIX=24"
                    echo "DEFROUTE=no"
                } >> "$BRFILE"
                ifup "$bridge"
                ip a flush "$ifname"
                brctl addif "$bridge" "$ifname"
                ip l set dev "$bridge" up
            fi
            ;;
    esac
}


function map {
    bridge=$(echo "$1" | awk  -F ";" '{print $1}')
    macVlan=$(echo "$1" | awk  -F ";" '{print $2}')
    mac=$(echo "$macVlan" | awk  -F "." '{print $1}')
    vlan=$(echo "$macVlan" | awk  -F "." '{print $2}')
    ipaddr=$(echo "$1" | awk  -F ";" '{print $3}')
    ifname=$(ip link show | grep -B1 "$mac" | awk -F ': ' 'NR==1{print $2}')
    if [ -n "$vlan" ]; then
        ifname="$ifname.$vlan"
    fi
    os=$(detect_os)
    create_bridge "$os" "$bridge" "$ifname" "$ipaddr"
}

function install_deps {
    os=$(detect_os)
    case "$os" in
        ubuntu16)
            apt update && apt upgrade -y
            apt install -y git libvirt-bin
            systemctl start libvirtd && systemctl enable libvirtd
            ;;

        suse)
            ;;
        centos)
            yum -y update > /dev/null
            yum -y install git > /dev/null
            yum -y groupinstall "Virtualization Host" > /dev/null
            systemctl start libvirtd && systemctl enable libvirtd
    esac 
}


#main

install_deps

# $1 is structured: br-name;mac.vlan;ip-addr
for mapping in $(echo "$1" | tr '+' '\n'); do
    echo "mapping $mapping"
    map "$mapping"
done
