#!/usr/bin/env python3

from netmiko.cisco import CiscoIosSSH
from getpass import getpass
import re


# password = getpass()

def reset_power_all_remote(hostname, username, password):
    net_connect = CiscoIosSSH(
        host=hostname,
        username=username,
        password=password,
        device_type='cisco_ios'
    )

    print("Connecting to {}".format(hostname))
    net_connect.find_prompt()
    interface_status = net_connect.send_command('show interface status', use_textfsm=True)

    # [print("{:^12} {:>4} {:^8} {:^8} {:^8} {}".format(i['port'],i['name'],i['vlan'],i['duplex'],i['speed'],i['type'])) for i in interface_status]
    access_ports = []
    [access_ports.append(i['port']) for i in interface_status if not re.search(r'\btrunk\b', i['vlan'])]

    for port in access_ports:
        print("Resetting Power for {}".format(port))
        net_connect.send_config_set('interface {}\n power inline never\n power inline auto'.format(port),
                                    exit_config_mode=False, cmd_verify=False)

    print("Exiting out of Global Config Mode")
    net_connect.exit_config_mode()
    print(
        "Disconnecting...\nWARNING: The configuration was NOT saved. Unless other changes were made, it does NOT need "
    net_connect.disconnect()
