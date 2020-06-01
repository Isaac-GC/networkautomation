#!/usr/bin/env python3

from netmiko.cisco import CiscoIosSSH
from netmiko.ssh_exception import NetmikoTimeoutException
from getpass import getpass
import re
import csv


# password = getpass()

def reset_power_all_remote(hostname, username, password):
    try:
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
        [access_ports.append(i['port']) for i in interface_status if
         not (re.search(r'\btrunk\b', i['vlan']) or re.search(r'\b1\b', i['vlan']))]

        for port in access_ports:
            print("Removing 'ip verify source' for port {}".format(port))
            net_connect.send_config_set('no ip verify source')
            print("Resetting Power for {}".format(port))
            net_connect.send_config_set('interface {}\n power inline never\n power inline auto'.format(port),
                                        exit_config_mode=False, cmd_verify=False)

        print("Exiting out of Global Config Mode")
        net_connect.exit_config_mode()
        print(
            "Disconnecting...\nWARNING: The configuration was saved. Unless other changes were made, it does NOT need be saved again")
        net_connect.disconnect()
    except NetmikoTimeoutException as e:
        print(e)

try:
    while True:
        print("\n")
        csv_file = str(input("Please enter the csv file to open: "))

        try:
            host_csv = open(csv_file, 'r')  # open up the selected csv file for read
            break
        except FileNotFoundError as e:
            print(e)

    username = str(input("Please enter your username: "))
    password = getpass()
    for host in csv.reader(host_csv, delimiter=','):
        reset_power_all_remote(host[0], username, password)

    host_csv.close()  # Close file to clean stuffs up
    print('Done with all/any configuration')  # Output the status that its done

except RuntimeError as e:
    print(e)
