import os
import time
import glob
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException

# Navigate to the URL and click the hospital search tab (left panel second menu)
def open_url_and_prepare(driver, url):
    driver.get(url)
    time.sleep(2)
    check_and_click(driver, '//a[@id="viewTab2"]')  # Clicks the 'Hospital/Pharmacy Search' tab
    time.sleep(1)

# Click an element using XPath if it's clickable, within a given timeout
def check_and_click(driver, xpath, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception:
        return False

# Wait for all .crdownload files to finish downloading (i.e., download is complete)
def wait_for_download(download_dir, timeout=30):
    for _ in range(timeout):
        if not any(f.endswith(".crdownload") for f in os.listdir(download_dir)):
            return True
        time.sleep(1)
    return False
