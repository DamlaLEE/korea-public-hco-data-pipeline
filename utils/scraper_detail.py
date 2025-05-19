# utils/scraper_detail.py

import os
import time
import re
import glob
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException

from utils.scraper_base import check_and_click

class HospitalDetailScraper:
    """
    Scraper class for fetching detailed information for hospitals.
    """

    def __init__(
        self,
        url: str,
        save_dir: str,
        target_categories: list = None,
        file_naming_rule: str = "hco_info_{category}_{timestamp}.csv"
    ):
        """
        Initialize the hospital detail scraper.

        Parameters:
            url (str): HIRA hospital search URL
            save_dir (str): Directory to save the CSV output
            target_categories (list): Hospital categories to include (e.g., ["상급종합병원", "종합병원"])
            file_naming_rule (str): Naming format for output CSV
        """
        self.url = url
        self.save_dir = save_dir
        self.target_categories = target_categories or ["상급종합병원", "종합병원"]
        self.file_naming_rule = file_naming_rule

        self.date_info = datetime.now().strftime("%Y%m%d_%H%M")
        os.makedirs(self.save_dir, exist_ok=True)

        self.driver = self._init_driver()

    def _init_driver(self):
        """Initialize Selenium Chrome WebDriver."""
        options = Options()
        options.add_argument("--start-maximized")
        return webdriver.Chrome(options=options)

    def get_hospital_categories(self):
        """Fetch category (id, name) from the HIRA website."""
        self.driver.get(self.url)
        check_and_click(self.driver, '//a[@id="viewTab2"]')
        time.sleep(1)
        labels = self.driver.find_elements(By.XPATH, '//ul[@id="hospType"]/li/label')
        return [
            (label.get_attribute("for"), label.text.strip())
            for label in labels if label.text.strip() in self.target_categories
        ]

    def scroll_and_collect_hospitals(self):
        """
        Scroll through the search result and collect all hospital entries with ykiho.

        Returns:
            List of dictionaries with hospital name and ykiho info.
        """
        prev_len = 0
        for i in range(100):
            a_tags = self.driver.find_elements(By.CSS_SELECTOR, "ul.mapResult li a.tit")
            if not a_tags:
                time.sleep(1)
                continue
            self.driver.execute_script("arguments[0].scrollIntoView(true);", a_tags[-1])
            time.sleep(1.2)
            new_tags = self.driver.find_elements(By.CSS_SELECTOR, "ul.mapResult li a.tit")
            if len(new_tags) == prev_len:
                break
            prev_len = len(new_tags)

        result_list = []
        for idx, tag in enumerate(new_tags, 1):
            name = tag.text.strip()
            onclick = tag.get_attribute("onclick")
            match = re.search(r'"(JDQ4[^"]+)"', onclick)
            ykiho = match.group(1) if match else None
            result_list.append({"index": idx, "name": name, "ykiho": ykiho})
        return result_list

    def fetch_detail_info(self, hospitals: list):
        """
        Use hospital ykiho to request additional info (staff count, specialties).
        """
        detail_url = "https://www.hira.or.kr/ra/hosp/hospInfoAjax.do"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": self.url
        }

        for item in hospitals:
            ykiho = item.get("ykiho")
            if not ykiho:
                item["doctor_info"] = "N/A"
                item["specialties"] = []
                continue

            try:
                res = requests.get(detail_url, params={"ykiho": ykiho}, headers=headers, timeout=10)
                res.encoding = "utf-8"
                soup = BeautifulSoup(res.text, "html.parser")

                td = soup.find("td", string=lambda t: t and "총 인원" in t)
                item["doctor_info"] = td.text.strip() if td else "N/A"

                ul_lists = soup.select("ul.pop_list_style")
                item["specialties"] = [li.text.strip() for li in ul_lists[0].select("li")] if ul_lists else []

            except Exception as e:
                item["doctor_info"] = f"Request failed: {e}"
                item["specialties"] = []

    def save_to_csv(self, hospitals: list, category_name: str):
        """Save hospital detail data to CSV file."""
        df = pd.DataFrame(hospitals)
        df = df[["index", "name", "ykiho", "doctor_info", "specialties"]]
        df["specialties"] = df["specialties"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        filename = self.file_naming_rule.format(category=category_name, timestamp=self.date_info)
        save_path = os.path.join(self.save_dir, filename)
        df.to_csv(save_path, index=False, encoding="utf-8-sig")
        print(f"✅ Saved: {save_path}")

    def run(self):
        """
        Run full detail scraper process for each hospital category.
        """
        categories = self.get_hospital_categories()
        for category_id, category_name in categories:
            print(f"\n🔍 Category: {category_name} ({category_id})")
            self.driver.get(self.url)
            check_and_click(self.driver, '//a[@id="viewTab2"]')
            time.sleep(1)

            checkbox = self.driver.find_element(By.ID, category_id)
            self.driver.execute_script("arguments[0].click();", checkbox)
            time.sleep(2)

            try:
                checkbox = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "chkAll_shwSbjtCds")))
                self.driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(1)
            except:
                print("⚠️ Department select-all checkbox not found.")

            search_button = self.driver.find_element(By.XPATH, '//a[contains(text(), "검색") and contains(@class, "btn_black")]')
            self.driver.execute_script("arguments[0].click();", search_button)
            time.sleep(3)

            hospitals = self.scroll_and_collect_hospitals()
            print(f"📦 Loaded hospitals: {len(hospitals)}")

            self.fetch_detail_info(hospitals)
            self.save_to_csv(hospitals, category_name)

        self.driver.quit()
