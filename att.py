import re
import sys
import datetime

from influxdb import InfluxDBClient

from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.common.exceptions import TimeoutException

if len(sys.argv) != 3:
    print('Usage: att.py <username> <password>')
    exit(0)

# Launch a headless Chrome session to scrape
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1366x768")

driver = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(driver, 20)

driver.get('https://www.att.com/my/#/login')

# Wait until login form loaded
try:
    wait.until(EC.presence_of_element_located((By.ID, 'login')))
except TimeoutException:
    driver.quit()
    sys.exit('Login failed')

# Submit login credentials
driver.find_element_by_id('userName').send_keys(sys.argv[1])
driver.find_element_by_class_name('lgwgPassword').send_keys(sys.argv[2])
driver.find_element_by_id('loginButton').click()

# Wait for main accounts page to load
try:
    wait.until(EC.url_to_be('https://www.att.com/my/#/accountOverview'))
    usage_str = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@ng-if='viewModel.pu_usage_cato']"))).text
except TimeoutException:
    driver.quit()
    sys.exit('Scraping main page failed')

# Extract usage data
match = re.fullmatch('(\d+\.\d+) of (\d+\.\d+).+', usage_str)
cur_usage = float(match.group(1))
cur_cap = float(match.group(2))

driver.quit()

# Get time info for InfluxDB
now = datetime.datetime.now()
month_number = "{:02d}".format(now.month)
year_number = "{:04d}".format(now.year)

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
            "cap": cur_cap
        }
    }
]

print(point)
