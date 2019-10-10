#!/usr/bin/python


import json
import sys


USER = 1


def make_job(host):
    return {
        "hardware": make_hardware_task(host),
        "software": make_software_task(host),
        "network": make_network_task(host),
        "access": make_access_task(host),
    }


def make_network_task(host):
    network_task = {
        "test_network_task_id": {
            "lab_token": "null"
        }
    }

    interface_config = {mac: [] for mac in host['interfaces'].keys()}  # all interfaces are empty
    for key in interface_config.keys():
        interface_config[key].append({
            "tagged": False,
            "vlan_id": 100
        })
        break  # we only want to set one interface, and we dont care which

    network_task["test_network_task_id"][host["hostname"]] = interface_config

    return network_task


def make_hardware_task(host):
    hardware_task = {
        "test_hardware_task_id": {
            "lab_token": "null",
            "image": host['centos_image'],
            "power": "on",
            "hostname": "some_hostname",
            "id": host['hostname'],
            "ipmi_create": True
        }
    }

    return hardware_task


def make_software_task(host):
    return {
        "test_software_task_id": {
            "lab_token": "null",
            "opnfv": {}
        }
    }


def make_access_task(host):
    return {
        "test_access_task_id": {
            "lab_token": "null",
            "access_type": "ssh",
            "revoke": False,
            "context": {
                "hosts": [host['hostname']],
                "key": "my_fake_ssh_key"
            },
            "user": USER
        },
        "test_access_task_id2": {
            "lab_token": "null",
            "access_type": "vpn",
            "revoke": False,
            "user": USER
        }
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Must provide Host definition from st2 datastore!")
        sys.exit(1)
    try:
        host_json = json.loads(sys.argv[1])
    except Exception as e:
        print("Host description is not valid JSON: " + str(e))
        sys.exit(2)
    print(json.dumps(
        make_job(host_json)
    ))
