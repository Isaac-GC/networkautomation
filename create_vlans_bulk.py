#!/usr/bin/env python3

import csv
import socket
import struct
import yaml
from getpass import getpass

from netmiko.cisco import CiscoIosSSH
from jinja2 import Environment, FileSystemLoader

username = 'cisco'
password = 'cisco'
host = '10.0.2.144'

# TODO
# - Create a function that outputs a number list menu
# - Move important functions to a utility file to be easily referenced


def cidr_to_netmask(net_bits):
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return netmask


def apply_template(template_dir, template_name, var_dict):
    # get template directory
    env = Environment(loader=FileSystemLoader(template_dir))

    # find the template by name with extension. Example: vlan-template.j2
    config_template = env.get_template(template_name)

    # Open the template and render the configuration
    config = config_template.render(template_var=var_dict)

    # Return it as is
    return config


def backup_running_config(hostname, username, password):
    net_connect = CiscoIosSSH(
        host=hostname,
        username=username,
        password=password,
        device_type='cisco_ios'
    )

    print("\n####################################################\n\nConnected to {"
          "}\n####################################################\n".format(host))
    print("Setting current terminal length to 0...")
    net_connect.send_command("terminal length 0")

    print("Backing up the configuration...")
    running_config = net_connect.send_command("show run")

    print("Disconnecting from the session")
    net_connect.disconnect()

    print("Done")
    return running_config


def apply_config_to_networkdevice(hostname, username, password, config):
    net_connect = CiscoIosSSH(
        host=hostname,
        username=username,
        password=password,
        device_type='cisco_ios'
    )

    print("\n####################################################\n\nConnected to {"
          "}\n####################################################\n".format(host))
    net_connect.find_prompt()

    print(config)

    while True:
        resp = str(input("Do you want to apply this configuration (Y/N): ")).lower()

        if resp[0] == 'y':
            print()
            net_connect.send_config_set(config, exit_config_mode=False, cmd_verify=False)
            print("Exiting out of Global Config Mode")
            net_connect.exit_config_mode()
            net_connect.send_command('wr me')  # write memory
            print("Successfully applied the configuration")
            break

        if resp[0] is 'n':
            print("Not applying the current configuration")
            net_connect.disconnect()
            break

        else:
            "Could not get that, please only enter Y or N"

    print(
        "Disconnecting...\nWARNING: Configuration has been saved")
    net_connect.disconnect()
    print("\n####################################################\n")


try:
    while True:
        print("\n")
        vtp_csv_file = str(input("Please enter the csv file to open: "))

        try:
            vtp_csv_content = open(vtp_csv_file, 'r') # open up the selected csv file for read
            break
        except FileNotFoundError as e:
            print(e)

    csv_config = ""
    for vlan in vtp_csv_content:
        vlan['subnet'] = cidr_to_netmask(vlan['subnet'])  # convert cidr (/24) to netmask (255.255.255.0)
        csv_config += apply_template('templates', 'vlan-template.j2', vlan)

        # print(base_vlan_config.render(vlan=vlan))

    host = str(input("Please enter the hostname or ip of the network device: "))
    username = str(input("Please enter your username: "))
    password = getpass()
    apply_config_to_networkdevice(host, username, password, csv_config)

    vtp_csv_content.close()  # Close file to clean stuffs up
    print('Done with all/any configuration')  # Output the status that its done

except RuntimeError as e:
    print(e)
