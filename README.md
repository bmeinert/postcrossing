![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)


# Postcrossing Global Logistics Analysis

A data science project to analyze worldwide postal transit times based on personal Postcrossing (https://postcrossing.com) exports. This project automates the parsing of JSON data, performs robust data cleansing, and calculates efficiency KPIs for international postal routes.

## Project Status
- [x] Data parsing of official Postcrossing JSON exports
- [x] Robust data cleansing & anonymization (removal of IDs/Usernames)
- [x] Calculation of logistics efficiency metrics (Days per 1,000 km)
- [ ] Global trajectory visualization (In Progress)

## Key Insights
The pipeline is designed to identify and analyze specific anomalies in global logistics:

* **USA (The 2025/26 'Black Hole'):** Analysis of significant transit bottlenecks and increased travel times for mail routes from Germany to the United States.
* **Russia (Geopolitical Impact):** Longitudinal study of logistics efficiency shifts following the onset of the conflict in Ukraine, documenting the transition from air to land-based transit.

## 🛠 Installation & Usage
The script requires Python 3.x and the `pandas` library.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bmeinert/postcrossing.git
2. **Prepare Data:**
   Place your raw JSON exports in the data/raw/ directory.
3. **Run the Pipeline:**
   ```bash
   python data_preprocessing.py

## Privacy & Data Ethics

This project strictly adheres to privacy standards and the Postcrossing Terms of Service:
* **No Scraping:** This tool does not scrape data from the Postcrossing website. It only processes official JSON export files provided to the user by the platform.
* **Anonymization:** All personally identifiable information (PII), such as usernames and specific postcard IDs, is removed during the cleaning process.
* **Aggregation:** Data is analyzed at a country-to-country level. No precise geographical coordinates (lat/long) are stored or shared.
* **Data Security:** Raw JSON files containing private information are excluded from this repository via `.gitignore`.



## License
The **code** in this repository is licensed under the [MIT License](LICENSE).  
The **data analysis, visualizations, and documentation** are licensed under 
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). 
Commercial use of the analysis results is prohibited without prior consent.