# pip install selenium==4.20.0
pip install webdriver-manager==4.0.1

import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

options = webdriver.ChromeOptions()
options.set_capability('goog:loggingPrefs', {"performance": "ALL", "browser": "ALL"})

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

#driver.set_page_load_timeout(10)

try:
    driver.get(' https://www.sofascore.com/fr/bournemouth-arsenal/Rkb#id:11352482')
except:
    pass

time.sleep(10)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

time.sleep(10)

try:
    consent = driver.find_element(By.XPATH, '//p[@class="fc-button-label"]').click()
except:
    pass

logs_raw = driver.get_log("performance")
logs = [json.loads(lr['message'])['message'] for lr in logs_raw]

for x in logs :     # looping through network responses
    if 'shotmap' in x['params'].get('headers', {}).get(':path', ''):    # if shotmap is in params get headers
        print(x['params'].get('headers', {}).get(':path', ''))
        break

shotmap = json.loads(driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': x['params']['requestId']})['body'])['shotmap']
print(shotmap)
