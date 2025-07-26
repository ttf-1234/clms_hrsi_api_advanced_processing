# CLMS API Advanced Processing Pipeline

## Overview

This repository provides an automated pipeline for downloading, processing, and filtering Copernicus Land Monitoring Service (CLMS) High Resolution Snow & Ice (HRSI) products. The workflow includes tile selection, data download, unzipping, mosaicking, reclassification, resampling, and cloud coverage filtering, all configurable via a central `config.py` file.

The pipeline is designed for reproducible, large-scale processing of Sentinel-2 based snow products for a user-defined area of interest (AOI).  
For more information about the CLMS snow products, visit the [Copernicus Land Monitoring Service Snow Products page](https://land.copernicus.eu/en/products/snow).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ttf-1234/clms_hrsi_api_advanced_processing
   cd clms_hrsi_api_advanced_processing
   ```

2. **Install dependencies and set up the environment:**

   **With Conda:**
   ```bash
   conda create -n clms_hrsi_api_advanced_processing python=3.10 -y
   conda activate clms_hrsi_api_advanced_processing
   conda install -y geopandas rasterio shapely requests fiona gdal pyogrio
   ```

   **Or with pip (if you do not use conda):**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install geopandas rasterio shapely requests fiona gdal pyogrio
   ```

## Required Input Data

- **Reference Raster:**  
  You must provide a reference raster file (e.g., a DEM or any raster) that defines your AOI. The path and CRS for this raster are set in `config.py`:
  ```python
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  reference_raster_path = os.path.join(BASE_DIR, "data/reference_raster/dem_rofental_100.asc")
  reference_raster_crs = "EPSG:32632"
  ```

- **CLMS Credentials:**  
  Access to the CLMS download API requires a valid username and password. You need a CLMS account to access the data. Register for free at [https://cryo.land.copernicus.eu/finder](https://cryo.land.copernicus.eu/finder). 
  These must be set in `config.py`:
  ```python
  clms_username = "your_username"
  clms_password = "your_password"
  ```

## Getting Started

1. **Configure your processing parameters and credentials in `config.py`.**


   In `config.py`, all paths are now resolved relative to the project root using `BASE_DIR`. You can set the following options to control the pipeline:

   - **Reference Raster:**
     - `reference_raster_path`: Path to your reference raster file (defines AOI), e.g. `os.path.join(BASE_DIR, "data/reference_raster/dem_rofental_100.asc")`.
     - `reference_raster_crs`: CRS of your reference raster.
     - `tile_txt_path`: Path where the list of relevant Sentinel-2 tiles will be saved.

   - **CLMS Credentials:**
     - `clms_username`: Your CLMS username.
     - `clms_password`: Your CLMS password.

   - **CLMS Product and Download Options:**
     - `clms_query_type`: `"query"`, `"download"`, or `"query_and_download"` (controls what the downloader does).
     - `clms_product`: List of product types to download (e.g., `["FSC", "PSA"]`).

   - **Time Period:**
     - `start_date`: Start date for data download (format: `YYYY-MM-DDTHH:MM:SSZ`).
     - `end_date`: End date for data download (format: `YYYY-MM-DDTHH:MM:SSZ`).

   - **Output Paths:**
     - `output_path_original`: Directory for original downloaded data, e.g. `os.path.join(BASE_DIR, "data/clms_data/original/")`.
     - `output_path_processed`: Directory for processed data, e.g. `os.path.join(BASE_DIR, "data/clms_data/processed/")`.

   - **Processing Options:**
     - `mosaic_output`: `True` to create mosaics, `False` to skip.
     - `reclassify`: `True` to reclassify rasters, `False` to skip.
     - `crop_resample`: `True` to resample/crop rasters to the reference grid, `False` to skip.
     - `filter_cc`: `True` to filter images by cloud coverage, `False` to skip.
     - `cc_threshold`: Maximum allowed cloud coverage (e.g., `0.2` for 20%).

   Adjust these parameters as needed for your specific use case.

2. **Run the full pipeline:**
   ```bash
   python main.py
   ```

## Original Repositories

This pipeline builds upon and automates the official [CLMS HRSI API client](https://github.com/eea/clms-hrsi-api-client-python) provided by the European Environment Agency.  
Tile system data is sourced from [Copernicus Sentinel-2 tiling grid](https://sentiwiki.copernicus.eu/__attachments/1692737/S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.zip?inst-v=7e368646-a179-477f-af62-26dcc645dd8a).


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