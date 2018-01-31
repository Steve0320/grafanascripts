import sys
import requests
import json
import datetime

from influxdb import InfluxDBClient

if len(sys.argv) != 3:
    print('Usage: att.py <username> <password>')
    exit(0)

# Use MyATT iOS API to retrieve usage data
api_url = 'https://m.att.com/best/resources/unauth/shared/native/overview/details'

# Set data specific to app
cookies = {
    'accessDomain': 'native',
    'myattappversion': '5.6.1',
    'RHR5': 'Y',
}

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-By': 'MYATT',
}

data = {
    'CommonData': {
            'Language': 'EN',
            'AppName': 'iOS-MYATT',
            'AppVersion': '5.6.1'
    },
    'UserId': sys.argv[1],
    'Password': sys.argv[2]
}

# Retrieve API data in JSON format
response = requests.post(
    api_url,
    headers=headers,
    cookies=cookies,
    data=json.dumps(data),
    timeout=30
).json()

# Error if API does not return success code
if response['Result']['Status'] != 'SUCCESS':
    exit('API request failed')

# Pull usage container
usage_card = response['NativeOverviewDetails']['cards'][2]['data']

# Format current date
now = datetime.datetime.now()
month_number = "{:02d}".format(now.month)
year_number = "{:02}".format(now.year)

# Extract relevant values
cur_usage = usage_card['pu_used']
cur_cap = usage_card['pu_alloted']
unit = usage_card['pu_uom']

# Normalize to GB
if unit == 'GB':
    cur_usage = cur_usage
elif unit == 'MB':
    cur_usage /= 1024
elif unit == 'TB':
    cur_usage *= 1024
else:
    cur_usage = -1

# Construct point
point = [
    {
        "measurement": "network_usage",
        "tags": {
            "network": "att",
            "year": year_number,
            "month": month_number
        },
        "fields": {
            "usage": cur_usage,
            "cap": cur_cap,
        }
    }
]

# Post data to InfluxDB
influx_db = InfluxDBClient('localhost', 8086, 'root', 'root', 'grafana')
influx_db.write_points(point)