import sys
import requests
import json

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
response = requests.post(api_url, headers=headers, cookies=cookies, data=json.dumps(data)).json()

#print(json.dumps(response, indent=4))

# Error if API does not return success code
if response['Result']['Status'] != 'SUCCESS':
    exit('API request failed')
