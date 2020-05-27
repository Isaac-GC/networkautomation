#!/usr/bin/env python3

import re

from getpass import getpass

from configparser import ConfigParser
from netmiko.cisco import CiscoIosSSH
from jinja2 import Template


console_output_tmpl = """
ip address: {{ device.ip }}
tacacs source vlan: {{ device.svlan }}
"""


def check_mgmt_vlan_by_source(username, password, list_of_ips):

    template = Template(console_output_tmpl)

    for ip in list_of_ips:

        t_source = ""

        net_connect = CiscoIosSSH(
            host=ip,
            username=username,
            password=password,
            device_type='cisco_ios'
        )

        t_source = net_connect.send_command("show run | inc ip tacacs source")

        vlan = re.search(r'[0-9]{3,4}', t_source)

        device_dict = {
            "ip": ip,
            "svlan": vlan
        }

        print(template.render(device=device_dict))

config = ConfigParser()
config.read('hosts')
idaho_vtp = config['VTPIdaho']

username = str(input("Please enter your username: "))
password = getpass()

check_mgmt_vlan_by_source(username, password, idaho_vtp)