## Notebook

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](
https://colab.research.google.com/github/advanced-computing/sparkly-pickle/blob/main/notebooks/analysis.ipynb
)

# Project 1 – Part 1: Proposal

**Group Name:** sparkly-pickle  
**Group Members:** Yiran Ge, Yizi Qu  

---

## 1. Dataset

**Name:** Motor Vehicle Collisions – Person Data  

**Link:** Motor Vehicle Collisions – Person Data  

**Description:**  
This dataset records individuals involved in New York City police-reported motor vehicle collisions. Each row represents one person involved in a crash (e.g., driver, passenger, pedestrian, or bicyclist). The dataset includes information on injury severity and road user type. The data is available starting from 2016, when NYC transitioned to an electronic crash reporting system.

---

## 2. Research Questions

1. How do injury and fatality outcomes differ across types of road users (pedestrians, cyclists, and motor vehicle occupants) in New York City since 2025?

2. Are there differences in the distribution of traffic-related injuries and fatalities across NYC boroughs since 2025?  
   - This question requires merging the *Person* dataset with the *Motor Vehicle Collisions – Crashes* dataset, which contains detailed location information, enabling borough-level and GIS-based analysis.

3. Do traffic-related injuries and fatalities exhibit temporal patterns over time (e.g., monthly trends) in New York City since 2025?

---

## 3. Notebook Link

https://colab.research.google.com/drive/1WEt7ZzIXHlwosCxOBvZGz_kDVjV4zd7u

---

## 4. Target Visualizations

### Visualization 1

**Type:** Stacked bar chart  

**Description:**  
A stacked bar chart comparing counts of injured versus killed individuals by road user type (pedestrian, cyclist, motor vehicle occupant). The visualization highlights differences in both total counts and outcome composition for each group since 2025.

---

### Visualization 2 (Planned)

**Type:** Faceted monthly time-series (line chart) by borough  

**Description:**  
This visualization will display monthly counts of injuries and fatalities across NYC boroughs since 2025 after merging the *Person* and *Crashes* datasets. The goal is to identify temporal patterns, seasonal effects, spikes, and borough-level differences. The group is still deciding on the final format (faceted plots, map-based visualization, or a combination of both).

---

## 5. Known Unknowns

- Not all person-level records may link cleanly to crash-level records, which could reduce the usable sample size for borough-level or GIS analyses.
- Some crash records may contain missing or incomplete location information, limiting mapping coverage.
- The datasets are based on police-reported crashes; underreporting or inconsistencies may exist depending on crash severity and reporting practices.

---

## 6. Anticipated Challenges

- Since the analysis focuses on data from 2025 onward, careful cleaning and standardization of date fields are required to ensure accurate monthly comparisons.
- Merging the person-level dataset with the crash-level dataset introduces a risk of double-counting; therefore, the merge process must be handled carefully to maintain consistency and data integrity.
