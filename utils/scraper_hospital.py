# utils/scraper_hospital.py
import os
import time
import glob
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException

from utils.scraper_base import open_url_and_prepare, check_and_click


class HospitalScraper:
    """
    Scraper class for downloading hospital data from the HIRA website.
    """

    def __init__(
        self,
        url: str,
        download_dir: str,
        log_dir: str,
        exclude_categories: list = None,
        file_naming_rule: str = "{category}_auto_{timestamp}{ext}"
    ):
        """
        Initialize scraper with config.

        Parameters:
            url (str): HIRA map URL
            download_dir (str): path to store downloaded Excel files
            log_dir (str): path to store failed logs
            exclude_categories (list): names of categories to skip (e.g., ['의원'])
            file_naming_rule (str): pattern for renaming files
        """
        self.url = url
        self.download_dir = download_dir
        self.log_dir = log_dir
        self.exclude_categories = exclude_categories or []
        self.file_naming_rule = file_naming_rule

        self.date_info = datetime.now().strftime("%Y%m%d_%H%M")
        self.failed_ids = []
        self.downloaded_file_paths = []

        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

        self.driver = self._init_driver()

    def _init_driver(self):
        """Set up Chrome WebDriver for automated download."""
        options = Options()
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--start-maximized")
        return webdriver.Chrome(options=options)

    def get_category_info(self):
        """Get hospital category (id, name) list from HIRA map."""
        open_url_and_prepare(self.driver, self.url)
        labels = self.driver.find_elements(By.XPATH, '//ul[@id="hospType"]/li/label')
        return [
            (label.get_attribute("for"), label.text.strip())
            for label in labels
            if label.text.strip() not in self.exclude_categories
        ]

    def download_all(self):
        """Iterate all categories and download Excel files."""
        category_info = self.get_category_info()

        for idx, (category_id, category_name) in enumerate(category_info):
            retry_attempted = False

            for attempt in range(2):
                try:
                    print(f"\n▶ [{idx+1}/{len(category_info)}] {category_name} ({category_id})")

                    if not check_and_click(self.driver, '//a[@id="viewTab2"]'):
                        raise Exception("Failed to click left panel tab")
                    time.sleep(1)

                    self.driver.execute_script(f'document.getElementById("{category_id}").click();')
                    time.sleep(1)

                    try:
                        dept_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.ID, "chkAll_shwSbjtCds")))
                        self.driver.execute_script("arguments[0].click();", dept_input)
                        time.sleep(1)
                    except:
                        print("⚠️ Department select-all checkbox not found.")

                    search_button = self.driver.find_element(By.XPATH, '//a[contains(text(), "검색") and contains(@class, "btn_black")]')
                    self.driver.execute_script("arguments[0].click();", search_button)
                    time.sleep(3)

                    try:
                        alert = self.driver.switch_to.alert
                        reason = f"Search alert: {alert.text}"
                        print(f"⚠️ Alert: {reason}")
                        alert.accept()
                        time.sleep(1)

                        dept_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.ID, "chkAll_shwSbjtCds")))
                        self.driver.execute_script("arguments[0].click();", dept_input)
                        time.sleep(1)

                        self.driver.execute_script("arguments[0].click();", search_button)
                        time.sleep(3)
                    except NoAlertPresentException:
                        pass

                    before_files = set(glob.glob(os.path.join(self.download_dir, "*.xls*")))

                    download_button = self.driver.find_element(By.XPATH, '//a[contains(@class,"excelDown")]')
                    self.driver.execute_script("arguments[0].click();", download_button)
                    print(f"🚀 Download requested: {category_name}")
                    time.sleep(35)

                    after_files = set(glob.glob(os.path.join(self.download_dir, "*.xls*")))
                    new_files = after_files - before_files

                    if new_files:
                        new_file = max(new_files, key=os.path.getctime)
                        self.downloaded_file_paths.append((new_file, category_name))
                        print(f"✅ Downloaded: {category_name}")
                    else:
                        raise Exception("No new file detected")

                    check_and_click(self.driver, '//button[contains(text(), "초기화")]', timeout=5)
                    time.sleep(2)
                    break

                except Exception as e:
                    reason = f"Exception: {str(e)}"
                    if not retry_attempted:
                        print(f"🔄 Retry: {reason}")
                        open_url_and_prepare(self.driver, self.url)
                        retry_attempted = True
                    else:
                        print(f"❌ Failed: {category_name}")
                        self.failed_ids.append((category_id, category_name, reason))
                        break

    def rename_files(self):
        """Rename downloaded files based on naming pattern."""
        print("\n🔄 Renaming downloaded files...")
        for file_path, category_name in self.downloaded_file_paths:
            ext = os.path.splitext(file_path)[-1]
            new_name = self.file_naming_rule.format(
                category=category_name,
                timestamp=self.date_info,
                ext=ext
            )
            new_path = os.path.join(self.download_dir, new_name)

            try:
                os.rename(file_path, new_path)
                print(f"✅ Renamed: {os.path.basename(file_path)} → {new_name}")
            except Exception as e:
                self.failed_ids.append(("", category_name, f"Rename failed: {str(e)}"))

    def save_log(self):
        """Save failure logs to text file in log_dir."""
        if self.failed_ids:
            log_path = os.path.join(self.log_dir, f"download_failed_log_{self.date_info}.txt")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"[{self.date_info}] Failed Downloads\n")
                f.write("=" * 50 + "\n")
                for cid, cname, reason in self.failed_ids:
                    f.write(f"- {cname} ({cid}): {reason}\n")
            print(f"\n📄 Saved log to: {log_path}")
        else:
            print("\n🎉 All downloads completed successfully!")

    def run(self):
        """Execute full scraping process."""
        self.download_all()
        self.rename_files()
        self.save_log()
        self.driver.quit()
