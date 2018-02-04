import sys
import subprocess
import pytz
import datetime
from influxdb import InfluxDBClient

if len(sys.argv) != 3:
    print('Usage: interface_usage.py <network name> <interface>')
    exit(0)

network = sys.argv[1]
interface = sys.argv[2]

output = subprocess.run(['vnstat', '--oneline', '-i', interface], stdout=subprocess.PIPE).stdout.decode()
output_array = output.split(';')

if output_array[0] != '1':
    exit('This script only supports vnStat output version 1')

cur_rx = output_array[8].split()
cur_tx = output_array[9].split()

# Standardize to bytes
# Should be cleaned up into a switch statement
if cur_rx[1] == 'KiB':
    cur_rx = round(float(cur_rx[0]) * (2 ** 10))
elif cur_rx[1] == 'MiB':
    cur_rx = round(float(cur_rx[0]) * (2 ** 20))
elif cur_rx[1] == 'GiB':
    cur_rx = round(float(cur_rx[0]) * (2 ** 30))
elif cur_rx[1] == 'TiB':
    cur_rx = round(float(cur_rx[0]) * (2 ** 40))
else:
    cur_rx = -1

if cur_tx[1] == 'KiB':
    cur_tx = round(float(cur_tx[0]) * (2 ** 10))
elif cur_tx[1] == 'MiB':
    cur_tx = round(float(cur_tx[0]) * (2 ** 20))
elif cur_tx[1] == 'GiB':
    cur_tx = round(float(cur_tx[0]) * (2 ** 30))
elif cur_tx[1] == 'TiB':
    cur_tx = round(float(cur_tx[0]) * (2 ** 40))
else:
    cur_tx = -1

# Calculate current month
tz = pytz.timezone('America/Los_Angeles')
now = datetime.datetime.now(tz)
month_number = "{:02d}".format(now.month)
year_number = "{:04d}".format(now.year)

# Construct point
point = [
    {
        "measurement": "interface_data_usage",
        "tags": {
            "network": network,
            "year": year_number,
            "month": month_number
        },
        "fields": {
            "usage_rx": cur_rx,
            "usage_tx": cur_tx,
        }
    }
]

# Post data to InfluxDB
influx_db = InfluxDBClient('localhost', 8086, 'root', 'root', 'grafana')
influx_db.write_points(point)