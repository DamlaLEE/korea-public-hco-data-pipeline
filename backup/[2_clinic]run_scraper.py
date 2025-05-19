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

# === utils 불러오기 ===
from utils.scraper_def import (
    open_url_and_prepare,
    wait_for_download,
    check_and_click
)

# === 1. Setup directories ===
base_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(base_dir, "data")
clinic_dir = os.path.join(download_dir, "clinic_data")
log_dir = os.path.join(base_dir, "log")

os.makedirs(download_dir, exist_ok=True)
os.makedirs(clinic_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# === 2. Chrome configuration ===
options = Options()
prefs = {
    "download.default_directory": clinic_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1
}
options.add_experimental_option("prefs", prefs)
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

url = "https://www.hira.or.kr/ra/hosp/getHealthMap.do?pgmid=HIRAA030002010000"
driver.get(url)

# === 3. Prepare page ===
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "hospType")))

# === 4. 진료과목 정보 수집 ===
tab_button = driver.find_element(By.ID, "viewTab2")
tab_button.click()
time.sleep(1)

clinic_label = driver.find_element(By.XPATH, '//label[text()="의원"]')
clinic_id = clinic_label.get_attribute("for")
driver.execute_script(f'document.getElementById("{clinic_id}").click();')
time.sleep(2)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "hospType2")))
labels_depart = driver.find_elements(By.XPATH, '//ul[@id="hospType2"]//label')

department_info = [
    (label.get_attribute("for"), label.text.strip())
    for label in labels_depart
    if label.text.strip() and label.text.strip() != "전체선택"
]

# === 5. Loop per department ===
failed_ids = []
mode = "auto"
date_info = datetime.now().strftime("%Y%m%d_%H%M")
downloaded_file_paths = []

for idx, (dept_id, dept_name) in enumerate(department_info):
    retry_attempted = False

    for attempt in range(2):
        try:
            print(f"\n▶ [{idx+1}/{len(department_info)}] {dept_name}")

            # 탭 다시 클릭
            tab_button = driver.find_element(By.ID, "viewTab2")
            tab_button.click()
            time.sleep(1)

            # 의원 선택
            driver.execute_script(f'document.getElementById("{clinic_id}").click();')
            time.sleep(2)

            # 진료과목 선택
            driver.execute_script(f'document.getElementById("{dept_id}").click();')
            time.sleep(1)

            # 검색 버튼 클릭
            search_button = driver.find_element(By.XPATH, '//a[contains(text(), "검색") and contains(@class, "btn_black")]')
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(5)

            try:
                alert = driver.switch_to.alert
                reason = f"Search triggered an alert: {alert.text}"
                print(f"⚠️ Alert: {reason}")
                alert.accept()
                failed_ids.append((dept_id, dept_name, reason))
                break
            except NoAlertPresentException:
                pass

            # 다운로드 시도 전 파일 목록
            before_files = set(glob.glob(os.path.join(clinic_dir, "*.xls*")))
            download_button = driver.find_element(By.XPATH, '//a[contains(@class,"excelDown")]')
            driver.execute_script("arguments[0].click();", download_button)
            print(f"🚀 Download requested: 의원 - {dept_name}")
            time.sleep(35)

            after_files = set(glob.glob(os.path.join(clinic_dir, "*.xls*")))
            new_files = after_files - before_files

            if new_files:
                new_file = max(new_files, key=os.path.getctime)
                downloaded_file_paths.append((new_file, dept_name))
                print(f"✅ Successfully downloaded: 의원 - {dept_name}")
            else:
                reason = "Download requested but no new file detected"
                print(f"⚠️ {reason}")
                failed_ids.append((dept_id, dept_name, reason))
                break

            break

        except Exception as e:
            reason = f"Unhandled exception: {str(e)}"
            if not retry_attempted:
                print(f"🔄 Retry: {reason}")
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "hospType")))
                retry_attempted = True
            else:
                print(f"❌ Failed: 의원 - {dept_name}")
                failed_ids.append((dept_id, dept_name, reason))
                break

# === 6. Rename files ===
print("\n🔄 Renaming downloaded files...")
for file_path, dept_name in downloaded_file_paths:
    ext = os.path.splitext(file_path)[-1]
    new_name = f"의원_{mode}_{dept_name}_{date_info}{ext}"
    new_path = os.path.join(clinic_dir, new_name)
    try:
        os.rename(file_path, new_path)
        print(f"✅ Renamed: {os.path.basename(file_path)} → {new_name}")
    except Exception as e:
        reason = f"File rename failed: {str(e)}"
        print(f"❌ {reason}")
        failed_ids.append(("", dept_name, reason))

# === 7. 종료 ===
driver.quit()

# === 8. 실패 로그 저장 ===
if failed_ids:
    log_path = os.path.join(log_dir, f"clinic_failed_log_{date_info}.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"[{date_info}] Failed Clinic Dept Downloads\n")
        f.write("=" * 50 + "\n")
        for did, dname, reason in failed_ids:
            f.write(f"- {dname} ({did}): {reason}\n")
    print(f"\n📄 Saved failed log to: {log_path}")
else:
    print("\n🎉 All clinic department downloads completed successfully!")
