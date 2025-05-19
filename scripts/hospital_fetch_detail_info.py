# scripts/hospital_fetch_detail_info.py

import os
import sys

# edit file_path to load utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.scraper_detail import HospitalDetailScraper

if __name__ == "__main__":
    # 📁 Base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 🌐 URL to access
    target_url = "https://www.hira.or.kr/ra/hosp/getHealthMap.do?pgmid=HIRAA030002010000"

    # 📂 Output directories
    save_dir = os.path.join(base_dir, "../data/hco_detail")

    # 📄 File naming rule
    filename_pattern = "hco_info_auto_{category}_{timestamp}.csv"

    # 🏥 Target hospital types (explicitly included)
    target_categories = ["상급종합병원", "종합병원"]

    # 🚀 Run the detail scraper
    scraper = HospitalDetailScraper(
        url=target_url,
        save_dir=save_dir,
        target_categories=target_categories,
        file_naming_rule=filename_pattern
    )
    scraper.run()
