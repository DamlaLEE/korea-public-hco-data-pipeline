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

from utils.scraper_def import (
    open_url_and_prepare,
    wait_for_download,
    check_and_click
)

# === 1. Setup download and log directories ===
base_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(base_dir, "data")
log_dir = os.path.join(base_dir, "log")

os.makedirs(download_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# === 2. Chrome configuration for automated downloads ===
options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1
}
options.add_experimental_option("prefs", prefs)
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

url = "https://www.hira.or.kr/ra/hosp/getHealthMap.do?pgmid=HIRAA030002010000"

# === 3. Load main page and prepare ===
open_url_and_prepare(driver, url)

# === 4. Fetch all hospital categories (id and name) ===
labels = driver.find_elements(By.XPATH, '//ul[@id="hospType"]/li/label')
category_info = [(label.get_attribute("for"), label.text.strip()) for label in labels]

# === 5. Extract "의원(clinic)" separately for special handling ===
regular_categories = [(cid, cname) for cid, cname in category_info if cname != "의원"]
clinic_category = [(cid, cname) for cid, cname in category_info if cname == "의원"]

failed_ids = []
mode = "auto"
date_info = datetime.now().strftime("%Y%m%d_%H%M")

# Track downloaded files for later renaming
downloaded_file_paths = []

# === 6. Download for regular hospital categories ===
for idx, (category_id, category_name) in enumerate(regular_categories):
    retry_attempted = False

    for attempt in range(2):
        try:
            print(f"\n▶ [{idx+1}/{len(regular_categories)}] {category_name} ({category_id})")

            if not check_and_click(driver, '//a[@id="viewTab2"]'):
                raise Exception("Failed to click left panel tab")
            time.sleep(1)

            driver.execute_script(f'document.getElementById("{category_id}").click();')
            time.sleep(1)

            try:
                dept_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "chkAll_shwSbjtCds")))
                driver.execute_script("arguments[0].click();", dept_input)
                time.sleep(1)
            except:
                print("⚠️ Could not find department 'select all' checkbox.")

            search_button = driver.find_element(By.XPATH, '//a[contains(text(), "검색") and contains(@class, "btn_black")]')
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(3)

            try:
                alert = driver.switch_to.alert
                reason = f"Search alert: {alert.text}"
                print(f"⚠️ {reason}")
                alert.accept()
                time.sleep(1)

                dept_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "chkAll_shwSbjtCds")))
                driver.execute_script("arguments[0].click();", dept_input)
                time.sleep(1)

                driver.execute_script("arguments[0].click();", search_button)
                time.sleep(3)
            except NoAlertPresentException:
                pass

            before_files = set(glob.glob(os.path.join(download_dir, "*.xls*")))

            download_button = driver.find_element(By.XPATH, '//a[contains(@class,"excelDown")]')
            driver.execute_script("arguments[0].click();", download_button)
            print(f"🚀 Download requested: {category_name}")
            time.sleep(35)

            after_files = set(glob.glob(os.path.join(download_dir, "*.xls*")))
            new_files = after_files - before_files

            if new_files:
                new_file = max(new_files, key=os.path.getctime)
                downloaded_file_paths.append((new_file, category_name))
                print(f"✅ Successfully downloaded: {category_name}")
            else:
                reason = "No new file detected after download"
                print(f"⚠️ {reason}")
                failed_ids.append((category_id, category_name, reason))
                break

            time.sleep(2)
            check_and_click(driver, '//button[contains(text(), "초기화")]', timeout=5)
            time.sleep(2)
            break

        except Exception as e:
            reason = f"Unhandled exception: {str(e)}"
            if not retry_attempted:
                print(f"🔄 Retry due to error: {reason}")
                open_url_and_prepare(driver, url)
                retry_attempted = True
            else:
                print(f"❌ Failed: {category_name} ({category_id})")
                failed_ids.append((category_id, category_name, reason))
                break

# === 7. Rename downloaded files ===
print("\n🔄 Renaming downloaded files...")
for file_path, category_name in downloaded_file_paths:
    ext = os.path.splitext(file_path)[-1]
    new_name = f"{category_name}_auto_{date_info}{ext}"
    new_path = os.path.join(download_dir, new_name)

    try:
        os.rename(file_path, new_path)
        print(f"✅ Renamed: {os.path.basename(file_path)} → {new_name}")
    except Exception as e:
        reason = f"File rename failed: {str(e)}"
        print(f"❌ {reason}")
        failed_ids.append(("", category_name, reason))

# === 8. Exit browser ===
driver.quit()

# === 9. Save failed log if any ===
if failed_ids:
    log_path = os.path.join(log_dir, f"download_failed_log_{date_info}.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"[{date_info}] Failed Downloads\n")
        f.write("=" * 50 + "\n")
        for cid, cname, reason in failed_ids:
            f.write(f"- {cname} ({cid}): {reason}\n")
    print(f"\n📄 Saved failed log to: {log_path}")
else:
    print("\n🎉 All downloads completed successfully!")
