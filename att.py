import sys
import requests
import json
import datetime
import pytz
from network_helpers import find_values

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
).text

# Format current date
tz = pytz.timezone('America/Los_Angeles')
now = datetime.datetime.now(tz)
month_number = "{:02d}".format(now.month)
year_number = "{:02}".format(now.year)

# Try to extract relevant values
try:
    status, cur_usage, cur_cap, unit = find_values(['Status', 'pu_used', 'pu_alloted', 'pu_uom'], response)
except ValueError:
    exit("API did not return a valid response")

# Error if API does not return success code
if status != 'SUCCESS':
    exit('API returned failure status')

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
