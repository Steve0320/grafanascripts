import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.chrome.options import Options

chrome_options = Options()
#chrome_options.add_argument("--headless")
#chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1366x768")

driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get('https://www.att.com/my/#/login')
#driver.find_element_by_id("userName").send_keys("test")

try:
    # Wait until login form loaded
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'login')))
except TimeoutException:
    driver.quit()
    exit(-1)

# Submit keys
driver.find_element_by_id('userName').send_keys('')
driver.find_element_by_class_name('lgwgPassword').send_keys('')
driver.find_element_by_id('loginButton').click()

# Add in exception for stupid AT&T popup stuff