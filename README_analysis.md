# 🏥 Public Healthcare Organization Data Analysis – Summary

This document summarizes the results of an exploratory data analysis (EDA) using public healthcare organization (HCO) data collected from HIRA. The goal is to demonstrate data engineering and analytical capabilities that align with business and customer success at Veeva Systems, including the use of web scraping, regex-based cleaning, and cloud storage readiness.

## 🔄 ETL Process Overview

The full pipeline, implemented in the `hco_data_pipeline.ipynb` notebook, follows these steps:

| Stage               | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| **Extract**        | Collected hospital, clinic, and tertiary hospital data via web scraping     |
| **Transform**      | Cleaned columns with regex, merged hospital data, parsed specialties         |
| **Load (Simulated)** | Simulated upload of cleaned datasets to AWS S3 bucket for cloud readiness |
| **Analysis**       | Performed analysis by category, region, and specialty distribution          |

---

## 📊 Key Analytical Summary (Tables + Insights)

### 📈 Analysis 1: Distribution by Category

**[Table 1] Number and Rate by Category**

```markdown
| category_en           | category_ko         | count | rate(%) |
|------------------------|----------------------|--------|----------|
| clinic                 | 의원                 | 37196  | 35.68    |
| pharmacy              | 약국                 | 25305  | 24.27    |
| dental_clinic         | 치과의원             | 19223  | 18.44    |
| oriental_clinic       | 한의원               | 14796  | 14.19    |
| public_health_center_branch | 보건진료소     | 1895   | 1.82     |
| hospital              | 병원                 | 1434   | 1.38     |
| nursing_hospital      | 요양병원             | 1332   | 1.28     |
| public_health_subcenter | 보건지소          | 1306   | 1.25     |
| oriental_hospital     | 한방병원             | 594    | 0.57     |
| general_hospital      | 종합병원             | 331    | 0.32     |
| psychiatric_hospital  | 정신병원             | 261    | 0.25     |
| public_health_center  | 보건소               | 246    | 0.24     |
| dental_hospital       | 치과병원             | 246    | 0.24     |
| tertiary_hospital     | 상급종합복장         | 47     | 0.05     |
| public_medical_center| 보건의료원           | 16     | 0.02     |
| birth_center          | 조산원               | 16     | 0.02     |
```

<p align="center">
  <img src="chart1.distribution_of_public_institutions_by_category.png" width="400" />
</p>

**🔎 Insight:** Clinics represent 35.7% of total HCOs, followed by pharmacies and dental clinics. Although general and tertiary hospitals account for a small fraction, they are essential due to their specialized services and staff size.

---

### 📈 Analysis 2: Distribution by Province

**[Table 2] Number and Rate by Province**

```markdown
| province_en | province_ko | count | rate(%) |
|-------------|--------------|--------|----------|
| Seoul       | 서울특별시    | 25149  | 24.13    |
| Gyeonggi    | 경기도        | 23782  | 22.81    |
| Busan       | 부산광역시    | 7323   | 7.02     |
| Gyeongnam   | 경상남도      | 5648   | 5.42     |
| Daegu       | 대구광역시    | 5611   | 5.38     |
| Incheon     | 인천광역시    | 5157   | 4.95     |
| Gyeongbuk   | 경상북도      | 4543   | 4.36     |
| Jeonbuk     | 전북특별자치도 | 3941   | 3.78     |
| Chungnam    | 충청남도      | 3873   | 3.72     |
| Jeonnam     | 전라남도      | 3480   | 3.34     |
| Daejeon     | 대전광역시    | 3166   | 3.04     |
| Gwangju     | 광주광역시    | 3061   | 2.94     |
| Chungbuk    | 충청북도      | 2943   | 2.82     |
| Gangwon     | 강원특별자치도 | 2691   | 2.58     |
| Ulsan       | 울산광역시    | 1879   | 1.80     |
| Jeju        | 제주특별자치도 | 1374   | 1.32     |
| Sejong      | 세종특별자치시 | 623    | 0.60     |
```

<p align="center">
  <img src="chart2.mumber_of_HCOs_by_province.png" width="600" />
</p>

**🔎 Insight:** Seoul and Gyeonggi together represent nearly 47% of HCOs. Regional concentration should be considered in outreach and service coverage planning.

---

### 🏥 Analysis 3: General & Tertiary Hospital Medical Staff

**[Table 3] Avg. Staff Count by Hospital Type**

```markdown
| category_en     | num_hospitals | num_dentists | num_doctors | num_korean_med | total_medical_staff |
|------------------|----------------|----------------|--------------|------------------|------------------------|
| general_hospital | 350            | 1.85           | 58.71        | 0.11             | 60.67                  |
| tertiary_hospital| 47             | 11.51          | 321.64       | 0.00             | 333.15                 |
```

<p align="center">
  <img src="d2f3dc28-44ab-4986-bbbd-53e967242324.png" width="650" />
</p>

**🔎 Insight:** Tertiary hospitals average 333 staff per institution—more than 5 times the size of general hospitals. These institutions dominate in medical capacity and specialization.

<p align="center">
  <img src="chart3.average_medical_staff_per_specialty_by_province.png" width="850" />
  <br/><br/>
  <img src="chart4.top10 specialties_avg_medical_staff_by_province.png" width="850" />
  <br/><br/>
  <img src="chart5.average_number_of_internal_medicinc_staff_per_hospital_by_province.png" width="850" />
</p>

**🔎 Insight:** These heatmaps reveal major differences in specialty staffing across provinces. Seoul stands out for its high concentration of internal medicine staff and top specialties. This variation supports the need for location-tailored coverage strategies.

---

### 📓 Appendix: Top Hospitals by Staff Count

**[Table 4] Top 10 Tertiary Hospitals by Total Staff**

<p align="center">
  <img src="06f2dbeb-a477-43e7-a7e8-36fb1bdb34b5.png" width="700" />
</p>

**[Table 5] Top 10 General Hospitals by Total Staff**

<p align="center">
  <img src="302bddc0-203a-46f6-a2a1-b7ee8b43eb79.png" width="700" />
</p>

---

**Author**: DS_Yujin LEE  
**Date**: 2025.05.14 ~ 2025.05.19  
**Version**: 1.0
