import requests
import urllib.request
import time
import json
from rich.table import Table
from rich.console import Console

# Created by Robert Gray-Christensen -- Feb 2021
#
# requires the requests and rich libraries in python3
#
# install using: pip install requests rich
#   or: python -m pip install requests rich
#

id_power_url = "https://api.idahopower.com/outagemap/api/outage/getcurrentoutageinformation"


def retrieve_url_jsondata(url):
	response = requests.get(id_power_url)

	if response.status_code != 200:
		print("\nResponse Status Code Returned: ", response.status_code)
		print("No error checking method was built for this")
		# print("\nThis script will try again in %d %s" % (num_of_sec, "seconds")) # Add method later
		print("Exiting Script") # TODO REMOVE LATER
		exit()

	elif response.status_code == 200:
		print("\nResponse Status Code Returned: ", response.status_code)
		print("Ingesting and transforming the data now")
		return json.loads(response.text)


# Parse Idaho Power Data
def parse_idpwr_data(json_data):
	d = {
		"data_type": "idahopower",
		"outage": []
	} # Reference Initial Data Structure

	try:
		outages = json_data['object']['outages']
	except KeyError:
		print("KeyError on \"json_data['object']['outages']\"")
		print("\nThe referenced API may have changed. Please check the API and try running the script again.")
		exit()

	for outage in outages:
		d['outage'].append({
			"planned":   		outage['isPlannedOutage'],
			"latitude":  		outage['latitude'],
			"longitude":  		outage['longitude'],
			"cause":      		outage['probableCause'],
			"status":     		outage['omsStatusDescription'],
			"start_time": 		outage['omsOutageStartDateMessage'],
			"outage_zips": 		[z['outageZipName'] for z in outage['outageZip']],
			"outage_counties": 	[z['outageCountyName'] for z in outage['outageCounty']],
			"outage_cities":	[z['outageCityName'] for z in outage['outageCity']]
		})

	return d


def print_formatted_results(json_data):

	console = Console()

	table = Table(show_header=True, header_style="bold magenta")
	table.add_column("Start Time", style="dim")
	table.add_column("Counties")
	table.add_column("Cities")
	table.add_column("Zipcodes")
	table.add_column("Planned")
	table.add_column("Cause")
	table.add_column("Status")

	delim = ","
	# If data is from Idaho Power
	if json_data['data_type'] == 'idahopower':
		# try:
		for row in json_data['outage']:
			table.add_row(
				row['start_time'],
				str(",".join([x for x in row['outage_counties']])),
				str(",".join([x for x in row['outage_cities']])),
				str(",".join([x for x in row['outage_zips']])),
				str(row['planned']),
				row['cause'],
				row['status'],
				)
		# except:
		# 	print("Couldn't parse the data")

	console.print(table)


json_data = retrieve_url_jsondata(id_power_url)
print_formatted_results(parse_idpwr_data(json_data))