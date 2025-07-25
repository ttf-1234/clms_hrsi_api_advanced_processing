# CLMS API Advanced Processing Pipeline

## Overview

This repository provides an automated pipeline for downloading, processing, and filtering Copernicus Land Monitoring Service (CLMS) High Resolution Snow & Ice (HRSI) products. The workflow includes tile selection, data download, unzipping, mosaicking, reclassification, resampling, and cloud coverage filtering, all configurable via a central `config.py` file. The pipeline is designed for reproducible, large-scale processing of Sentinel-2 based snow products for a user-defined area of interest (AOI).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ttf-1234/clms_hrsi_api_advanced_processing
   cd clms_hrsi_api_advanced_processing
   ```

2. **Install dependencies and set up the environment:**
   ```bash
   bash setup.sh
   ```

## Required Input Data

- **Reference Raster:**  
  You must provide a reference raster file (e.g., a DEM or other georeferenced raster) that defines your AOI. The path and CRS for this raster are set in `config.py`:
  ```python
  reference_raster_path = "./../data/reference_raster/dem_rofental_100.asc"
  reference_raster_crs = "EPSG:32632"
  ```

- **CLMS Credentials:**  
  Access to the CLMS download API requires a valid username and password. These must be set in `config.py`:
  ```python
  clms_username = "your_username"
  clms_password = "your_password"
  ```

## Data Source and Usage Policy

The Copernicus Land Monitoring Service data used in this pipeline is provided under the principle of full, open, and free access, as established by the Copernicus data and information policy ([Regulation (EU) No 1159/2013](http://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32013R1159)).  
Key conditions for use include:

- **Source Attribution:**  
  When distributing or sharing Copernicus data or derived information, you must clearly indicate the source as Copernicus and the European Union.

- **No Official Endorsement:**  
  Do not imply that your activities or products are officially endorsed by the European Union.

- **Modification Disclosure:**  
  If you adapt or modify the data, you must clearly state this in any communication or publication.

- **Ownership:**  
  The data remain the sole property of the European Union. Any information and data produced in the framework of this pipeline are also the property of the European Union. Any communication or publication must acknowledge that the data were produced “with funding by the European Union”.

## Original Repositories

This pipeline builds upon and automates the official [CLMS HRSI API client](https://github.com/eea/clms-hrsi-api-client-python) provided by the European Environment Agency.  
Tile system data is sourced from [Copernicus Sentinel-2 tiling grid](https://sentiwiki.copernicus.eu/__attachments/1692737/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.zip?inst-v=7e368646-a179-477f-af62-26dcc645dd8a).

## Getting Started

1. **Configure your processing parameters and credentials in `config.py`.**

2. **Run the full pipeline:**
   ```bash
   python main.py
   ```

## Acknowledgements

This work uses Copernicus data and information funded by the