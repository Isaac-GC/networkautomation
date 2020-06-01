#!/usr/bin/env python3

from netmiko.cisco import CiscoIosSSH
from getpass import getpass
import csv


def save_config(hostname, username, password):
    net_connect = CiscoIosSSH(
        host=hostname,
        username=username,
        password=password,
        device_type='cisco_ios'
    )

    print("Connecting to {}".format(hostname))
    net_connect.find_prompt()
    hostname = net_connect.send_command("show run | inc hostname")
    print("Writing Memory for {}".format(hostname.split()[1]))
    interface_status = net_connect.send_command('write memory')
    net_connect.disconnect()
    print("Disconnected...")


try:
    while True:
        csv_file = str(input("Please enter the csv file to open: "))

        try:
            host_csv = open(csv_file, 'r')  # open up the selected csv file for read
            break
        except FileNotFoundError as e:
            print(e)

    username = str(input("Please enter your username: "))
    password = getpass()
    for host in csv.reader(host_csv, delimiter=','):
        print(host[0])
        save_config(host[0], username, password)

    host_csv.close()  # Close file to clean stuffs up
    print('Done with all/any configuration')  # Output the status that its done

except RuntimeError as e:
    print(e)
