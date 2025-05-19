# utils/scraper_clinic.py

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

from utils.scraper_base import open_url_and_prepare, check_and_click

class ClinicScraper:
    """
    Scraper class for downloading clinic data by department from the HIRA website.
    """

    def __init__(
        self,
        url: str,
        download_dir: str,
        log_dir: str,
        file_naming_rule: str = "clinic_{dept}_auto_{timestamp}{ext}"
    ):
        """
        Initialize the clinic scraper.

        Parameters:
            url (str): Target URL to scrape
            download_dir (str): Directory to save downloaded files
            log_dir (str): Directory to save logs
            file_naming_rule (str): Pattern to rename downloaded files
        """
        self.url = url
        self.download_dir = download_dir
        self.log_dir = log_dir
        self.file_naming_rule = file_naming_rule

        self.date_info = datetime.now().strftime("%Y%m%d_%H%M")
        self.failed_ids = []
        self.downloaded_file_paths = []

        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

        self.driver = self._init_driver()

    def _init_driver(self):
        """Initialize Selenium Chrome WebDriver."""
        options = Options()
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,  # ✨ 핵심
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_settings.popups": 0,
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        return webdriver.Chrome(options=options)

    def get_departments(self):
        """Fetch all department ids and names for clinics."""
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "hospType")))

        tab_button = self.driver.find_element(By.ID, "viewTab2")
        tab_button.click()
        time.sleep(1)

        clinic_label = self.driver.find_element(By.XPATH, '//label[text()="건강의원"]')
        clinic_id = clinic_label.get_attribute("for")
        self.driver.execute_script(f'document.getElementById("{clinic_id}").click();')
        time.sleep(2)

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "hospType2")))
        labels_depart = self.driver.find_elements(By.XPATH, '//ul[@id="hospType2"]//label')

        self.clinic_id = clinic_id
        return [
            (label.get_attribute("for"), label.text.strip())
            for label in labels_depart
            if label.text.strip() and label.text.strip() != "전체선택"
        ]

    def download_all(self):
        """Download clinic files by department."""
        departments = self.get_departments()

        for idx, (dept_id, dept_name) in enumerate(departments):
            retry_attempted = False

            for attempt in range(2):
                try:
                    print(f"\n▶ [{idx+1}/{len(departments)}] {dept_name}")

                    tab_button = self.driver.find_element(By.ID, "viewTab2")
                    tab_button.click()
                    time.sleep(1)

                    self.driver.execute_script(f'document.getElementById("{self.clinic_id}").click();')
                    time.sleep(2)

                    self.driver.execute_script(f'document.getElementById("{dept_id}").click();')
                    time.sleep(1)

                    search_button = self.driver.find_element(By.XPATH, '//a[contains(text(), "검색") and contains(@class, "btn_black")]')
                    self.driver.execute_script("arguments[0].click();", search_button)
                    time.sleep(5)

                    try:
                        alert = self.driver.switch_to.alert
                        print(f"⚠️ Alert: {alert.text}")
                        alert.accept()
                        self.failed_ids.append((dept_id, dept_name, alert.text))
                        break
                    except NoAlertPresentException:
                        pass

                    before_files = set(glob.glob(os.path.join(self.download_dir, "*.xls*")))
                    download_button = self.driver.find_element(By.XPATH, '//a[contains(@class,"excelDown")]')
                    self.driver.execute_script("arguments[0].click();", download_button)
                    print(f"🚀 Download requested: 의원 - {dept_name}")
                    time.sleep(35)

                    after_files = set(glob.glob(os.path.join(self.download_dir, "*.xls*")))
                    new_files = after_files - before_files

                    if new_files:
                        new_file = max(new_files, key=os.path.getctime)
                        self.downloaded_file_paths.append((new_file, dept_name))
                        print(f"✅ Downloaded: 의원 - {dept_name}")
                    else:
                        raise Exception("No new file detected")

                    break

                except Exception as e:
                    reason = f"Exception: {str(e)}"
                    if not retry_attempted:
                        print(f"🔄 Retry: {reason}")
                        self.driver.get(self.url)
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "hospType")))
                        retry_attempted = True
                    else:
                        print(f"❌ Failed: 의원 - {dept_name}")
                        self.failed_ids.append((dept_id, dept_name, reason))
                        break

    def rename_files(self):
        """Rename downloaded clinic files."""
        print("\n🔄 Renaming downloaded files...")
        for file_path, dept_name in self.downloaded_file_paths:
            ext = os.path.splitext(file_path)[-1]
            new_name = self.file_naming_rule.format(dept=dept_name, timestamp=self.date_info, ext=ext)
            new_path = os.path.join(self.download_dir, new_name)

            try:
                os.rename(file_path, new_path)
                print(f"✅ Renamed: {os.path.basename(file_path)} → {new_name}")
            except Exception as e:
                self.failed_ids.append(("", dept_name, f"Rename failed: {str(e)}"))

    def save_log(self):
        """Save log of failed downloads."""
        if self.failed_ids:
            log_path = os.path.join(self.log_dir, f"clinic_failed_log_{self.date_info}.txt")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"[{self.date_info}] Failed Clinic Dept Downloads\n")
                f.write("=" * 50 + "\n")
                for did, dname, reason in self.failed_ids:
                    f.write(f"- {dname} ({did}): {reason}\n")
            print(f"\n📄 Saved log: {log_path}")
        else:
            print("\n🎉 All clinic department downloads completed successfully!")

    def run(self):
        """Run the full clinic scraping workflow."""
        self.download_all()
        self.rename_files()
        self.save_log()
        self.driver.quit()
