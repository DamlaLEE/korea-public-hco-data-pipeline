# 📌 Project Purpose

This project was designed to directly align with the key requirements of the **Data Analyst – OpenData Commercial** position at Veeva Systems. It showcases my ability to build a robust **ETL (Extract, Transform, Load)** pipeline using public data sources, with a strong emphasis on **web scraping**, **data cleaning using regular expressions**, and the ability to scale processes to cloud-based environments.

In addition to technical execution, this project reflects my understanding of **Veeva’s mission to deliver trusted, high-quality data to life sciences customers**. By working with real-world healthcare organization data in Korea, this work demonstrates how data pipelines can support informed decisions about provider coverage and commercial strategy.

> This portfolio was self-initiated to illustrate my fit for Veeva Systems, and is not an official project from the company.

---

## 📟 Project Overview

**Project Name**: Public Healthcare Organization Data Webscraping Project

This project collects structured public hospital and clinic information from Korea's Health Insurance Review and Assessment Service (HIRA) using automated **web scraping**. The raw data is processed using **regular expressions** to clean and standardize key features, and then transformed into actionable insights about the Korean healthcare ecosystem.

### ✔️ Collected Information:
- **Basic**: `hospital_name`, `category`, `phone`, `postal_code`, `address`, `homepage_address`
- **Extended**: `ykiho`, `doctor_info`, `specialties`

---

## 🤩 Tech Stack

- **Web Scraping**: Selenium, BeautifulSoup, requests
- **Data Processing**: pandas, re (Regular Expressions)
- **Other**: os, time, datetime, glob
- **Cloud Integration**: AWS S3 (via `boto3`, simulated upload)

---

## 🛠️ Project Workflow (ETL Process)

### 1. Extract (Web Scraping)
- Download full HCO data across 10 major types (excluding clinics)
- Clinic-specific download by department (24 total)
- Detail-level scraping for large hospitals (doctors, specialties)

### 2. Transform (Data Cleaning)
- Rename all columns from Korean to English
- Apply regular expressions to clean unstructured fields (e.g., doctor counts)
- Extract province and city from address strings
- Normalize specialty columns to consistent format (snake_case)

### 3. Load (Cloud Readiness)
- Simulate file upload to AWS S3 using boto3
- Demonstrates cloud deployment preparation

---

## 📁 Project Structure (Detailed)

```
project_root/
├── scripts/                              # Web scraping entry point scripts
│   ├── hospital_download_all.py          # Download all HCOs excluding clinics
│   ├── clinic_download_by_dept.py        # Clinic-specific download by departments
│   └── hospital_fetch_detail_info.py     # Fetch doctor/specialty info for major hospitals
│
├── utils/                                # Utility modules (reusable functions and scrapers)
│   ├── scraper_base.py                   # Shared utility functions (e.g., click handler)
│   ├── scraper_clinic.py                 # Scraper class for clinics
│   ├── scraper_hospital.py               # Scraper class for all hospitals (excluding clinics)
│   └── scraper_detail.py                 # Scraper for detailed hospital information (e.g., doctors, specialties)
│
├── data/                                 # Raw and processed data files (CSV)
│   ├── hco/                              # Raw scraped files1_hco
│   ├── clinic/                           # Raw scraped files2_clinic
│   ├── hco_detail/                       # Raw scraped files3_hco_detail
│   └── cleaned/                          # Cleaned and transformed files
│
├── config/                               # Configuration files for mapping or constants used in analysis
│   └── mapping_info.py                   # Contains reference mappings (e.g., hospital types, regional codes)
│
├── images/                               # Plots and visualizations for README_analysis
│
├── hco_data_pipeline.ipynb               # Full pipeline demonstration: load, clean, analyze, and mock-upload
├── README.md                             # Project overview and scraping pipeline focus
├── README_analysis.md                    # Analysis result and business insight focus
```

---

## 🎯 Highlights: How This Matches Veeva’s Vision

- ✅ **Web Scraping Expertise**: Automates data extraction from public sites with complex structure
- ✅ **Regex Mastery**: Uses regular expressions to clean and normalize unstructured fields
- ✅ **ETL End-to-End Ownership**: All steps from raw data to insight
- ✅ **Commercial Relevance**: Targets high-volume hospitals & specialties aligned with HCO profiling
- ✅ **Cloud-Aware**: Simulates AWS S3 upload to prepare for scalable environments

---

## 📟 Metadata

- **Author**: DS_Yujin LEE  
- **Date**: 2025.05.14 ~ 2025.05.19  
- **Version**: v1.0  
- **Source**: [hira.or.kr](http://www.hira.or.kr)

---

> See `README_analysis.md` for full analysis summary with visualizations and insights.
