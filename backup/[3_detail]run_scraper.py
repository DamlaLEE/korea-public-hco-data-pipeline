import os
import time
import re
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === 1. Set environment ===
mode = "auto"
date_info = datetime.now().strftime("%Y%m%d_%H%M")
base_dir = os.path.dirname(os.path.abspath(__file__))
save_dir = os.path.join(base_dir, "data", "hco_detail")
os.makedirs(save_dir, exist_ok=True)

# === 2. Set up Chrome options ===
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

url = "https://www.hira.or.kr/ra/hosp/getHealthMap.do?pgmid=HIRAA030002010000"
driver.get(url)

# === 3. Click hospital search tab ===
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "viewTab2"))).click()
time.sleep(1)

# === 4. Fetch hospital categories dynamically ===
labels = driver.find_elements(By.XPATH, '//ul[@id="hospType"]/li/label')
category_info = [(label.get_attribute("for"), label.text.strip()) for label in labels]
regular_categories = [(cid, cname) for cid, cname in category_info if cname in ("상급종합병원", "종합병원")]

# === 5. Iterate over categories ===
for category_id, category_name in regular_categories:
    print(f"\n🔍 Category: {category_name} ({category_id})")

    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "viewTab2"))).click()
    time.sleep(1)

    # === 6. Click category checkbox ===
    checkbox = driver.find_element(By.ID, category_id)
    driver.execute_script("arguments[0].click();", checkbox)
    time.sleep(2)

    # === 7. Select all departments ===
    try:
        checkbox = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "chkAll_shwSbjtCds")))
        driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(1)
    except:
        print("⚠️ Department select-all checkbox not found.")

    # === 8. Click search button ===
    search_button = driver.find_element(By.XPATH, '//a[contains(text(), "검색") and contains(@class, "btn_black")]')
    driver.execute_script("arguments[0].click();", search_button)
    time.sleep(3)

    # === 9. Scroll to load all results ===
    # === 9. Scroll to load all results ===
    prev_len = 0
    for i in range(100):  # 반복 횟수는 충분히 크게
        a_tags = driver.find_elements(By.CSS_SELECTOR, "ul.mapResult li a.tit")
        if not a_tags:
            time.sleep(1)
            continue

        # 마지막 요소를 화면에 보이도록 스크롤
        driver.execute_script("arguments[0].scrollIntoView(true);", a_tags[-1])
        time.sleep(1.2)

        new_tags = driver.find_elements(By.CSS_SELECTOR, "ul.mapResult li a.tit")
        print(f"🔄 Scroll {i+1}: {len(new_tags)} items")

        if len(new_tags) == prev_len:
            print(f"✅ Scroll finished at: {len(new_tags)}")
            break
        prev_len = len(new_tags)

    print(f"📦 Total hospitals loaded for {category_name}: {len(a_tags)}")

    # === 10. Extract hospital data ===
    result_list = []
    for idx, tag in enumerate(a_tags, 1):
        name = tag.text.strip()
        onclick = tag.get_attribute("onclick")
        match = re.search(r'"(JDQ4[^"]+)"', onclick)
        ykiho = match.group(1) if match else None

        result_list.append({
            "index": idx,
            "name": name,
            "onclick": onclick,
            "ykiho": ykiho
        })

    # === 11. Fetch detail data using ykiho ===
    detail_url = "https://www.hira.or.kr/ra/hosp/hospInfoAjax.do"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": url
    }

    for item in result_list:
        ykiho = item.get("ykiho")
        if not ykiho:
            item["doctor_info"] = "❌ No ykiho"
            item["specialties"] = []
            continue

        try:
            res = requests.get(detail_url, params={"ykiho": ykiho}, headers=headers, timeout=10)
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")

            td = soup.find("td", string=lambda t: t and "총 인원" in t)
            item["doctor_info"] = td.text.strip() if td else "❌ No doctor info"

            ul_lists = soup.select("ul.pop_list_style")
            item["specialties"] = [li.text.strip() for li in ul_lists[0].select("li")] if len(ul_lists) > 0 else []
  

        except Exception as e:
            item["doctor_info"] = f"❌ Request failed: {e}"
            item["specialties"] = []

    # === 12. Save to CSV ===
    df = pd.DataFrame(result_list)
    df = df[["index", "name", "onclick", "ykiho", "doctor_info", "specialties"]]
    df["specialties"] = df["specialties"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

    filename = f"hco_info_{mode}_{category_name}_{date_info}.csv"
    save_path = os.path.join(save_dir, filename)
    df.to_csv(save_path, index=False, encoding="utf-8-sig")
    print(f"✅ Saved: {save_path}")

# === 13. Close driver ===
driver.quit()
