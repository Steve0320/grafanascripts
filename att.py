import requests
import json
import sys
import datetime

login_url = 'https://att.com'
api_url = 'https://www.att.com/apis/maps'

# Preserve session cookies (particularly _MyAccountWeb_session)
session = requests.session()

# Login to set session cookies
#result = session.post(
#    login_url,
#    data={'user': sys.argv[1], 'passwd': sys.argv[2]}
#)

#print(session.cookies['_MyAccountWeb_session'])

# Retrieve API data in JSON format
api_response = session.get(api_url)
print(api_response.text)