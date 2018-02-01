import requests
import json
import sys
import datetime
import pytz
from influxdb import InfluxDBClient

if len(sys.argv) != 3:
    print('Usage: comcast.py <username> <password>')
    exit(0)

login_url = 'https://login.comcast.net/login?r=comcast.net&s=oauth&continue=https%3A%2F%2Foauth.xfinity.com%2Foauth%2Fauthorize%3Fclient_id%3Dmy-account-web%26prompt%3Dlogin%26redirect_uri%3Dhttps%253A%252F%252Fcustomer.xfinity.com%252Foauth%252Fcallback%26response_type%3Dcode%26state%3D%2523%252F%26response%3D1'
api_url = 'https://customer.xfinity.com/apis/services/internet/usage'

# Preserve session cookies (particularly _MyAccountWeb_session)
session = requests.session()

# Login to set session cookies
result = session.post(
    login_url,
    data={'user': sys.argv[1], 'passwd': sys.argv[2]}
)

# Retrieve API data in JSON format
api_response = session.get(api_url).json()

# Calculate current month
tz = pytz.timezone('America/Los_Angeles')
now = datetime.datetime.now(tz)
month_number = "{:02d}".format(now.month)
year_number = "{:04d}".format(now.year)

cur_month = None

# Find current month
date = "{:s}/01/{:s}".format(month_number, year_number)
for month in api_response['usageMonths']:
    if month['startDate'] == date:
        cur_month = month
        break

# Error if month not found
if cur_month is None:
    exit('Current month not found in API response')

# Extract values to insert into database
cur_usage = cur_month['homeUsage']
cur_cap = cur_month['allowableUsage']
unit = cur_month['unitOfMeasure']
c_remaining = api_response['courtesyRemaining']
c_total = api_response['courtesyAllowed']

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
            "network": "comcast",
            "year": year_number,
            "month": month_number
        },
        "fields": {
            "usage": cur_usage,
            "cap": cur_cap,
            "courtesy_remaining": c_remaining,
            "courtesy_total": c_total
        }
    }
]

# Post data to InfluxDB
influx_db = InfluxDBClient('localhost', 8086, 'root', 'root', 'grafana')
influx_db.write_points(point)
