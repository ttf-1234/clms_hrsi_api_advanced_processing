# CLMS API Advanced Processing Pipeline

## Overview

This repository provides an automated, object-oriented pipeline for downloading, processing, and filtering Copernicus Land Monitoring Service (CLMS) High Resolution Snow & Ice (HRSI) products. The workflow includes tile selection, data download, unzipping, mosaicking, reclassification, resampling, and cloud coverage filtering, all configurable via a central `config.py` file in the project root.

The pipeline is based on and extends the official CLMS HRSI API client:
- [eea/clms-hrsi-api-client-python](https://github.com/eea/clms-hrsi-api-client-python)

Example reference rasters are provided in `data/reference_raster/`. Use these for testing or as templates for your own AOI.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ttf-1234/clms_hrsi_api_advanced_processing
   cd clms_hrsi_api_advanced_processing
   ```

2. **Set up your Python environment and install dependencies:**

   **With Conda:**
   ```bash
   conda create -n clms_hrsi_api_advanced_processing python=3.10 -y
   conda activate clms_hrsi_api_advanced_processing
   conda install -y geopandas rasterio shapely requests fiona gdal pyogrio
   ```

   **Or with pip:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install geopandas rasterio shapely requests fiona gdal pyogrio
   ```

## Configuration

Edit `config.py` in the project root to set all pipeline options. Example:

```python
from config import CLMSConfig

config = CLMSConfig(
    reference_rasters=[
        {"name": "dem_rofental_100.asc", "crs": "EPSG:32632"},
        {"name": "dem_guadalfeo_100.asc", "crs": "EPSG:32630"},
        # Add more as needed
    ],
    clms_username="your_username",
    clms_password="your_password",
    clms_query_type="query_and_download",  # "query", "download", or "query_and_download"
    clms_product=["FSC"],  # Allowed: ["FSC", "PSA", "SWS", "WDS", "GFSC"]
    start_date="2023-07-01T00:00:00Z",
    end_date="2023-07-02T23:59:59Z",
    reference_raster_dir="data/reference_raster/",
    output_path_original="data/clms_data/original/",
    output_path_processed="data/clms_data/processed/",
    mosaic_output=True,
    reclassify=True,
    crop_resample=True,
    filter_cc=False,
    cc_threshold=0.2,
)
```

## Usage

Run the pipeline from the project root:

```bash
python main.py
```

This will execute all steps: download, tile determination, mosaicking, reclassification, resampling, and cloud filtering, according to your configuration.

## Input Data

- **Reference Rasters:** Place your DEMs or other reference rasters in `data/reference_raster/` and list them in `config.py`.
- **CLMS Credentials:** Register for a free account at [Copernicus CryoLand Finder](https://cryo.land.copernicus.eu/finder) and set your username/password in `config.py`.

## Pipeline Structure

- `main.py`: Entry point for running the pipeline.
- `config.py`: User-editable configuration file.
- `clms_pipeline/`: Contains all pipeline logic and step classes.
    - `pipeline.py`: Orchestrates the workflow.
    - `steps/`: Contains classes for each processing step.
    - `utils.py`: (Optional) Utility functions.

## Data Source and Usage Policy

Copernicus Land Monitoring Service data is provided under full, open, and free access ([Regulation (EU) No 1159/2013](http://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32013R1159)).

**Key conditions:**
- **Source Attribution:** Always credit Copernicus and the European Union.
- **No Official Endorsement:** Do not imply EU endorsement.
- **Modification Disclosure:** Clearly state if you adapt or modify the data.
- **Ownership:** Data remains property of the European Union. Acknowledge funding in any communication or publication.