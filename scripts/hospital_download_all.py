# scripts/hospital_download_all.py
import os
import sys

# edit file_path to load utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.scraper_hospital import HospitalScraper

if __name__ == "__main__":
    # 🧾 Base settings
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 📌 Parameters (editable)
    target_url = "https://www.hira.or.kr/ra/hosp/getHealthMap.do?pgmid=HIRAA030002010000"
    download_path = os.path.join(base_dir, "../data/hco")
    log_path = os.path.join(base_dir, "../log/hco")
    exclude = ["의원"]
    filename_pattern = "{category}_auto_{timestamp}{ext}"  # Customizable

    # 🚀 Run scraper
    scraper = HospitalScraper(
        url=target_url,
        download_dir=download_path,
        log_dir=log_path,
        exclude_categories=exclude,
        file_naming_rule=filename_pattern
    )
    scraper.run()
