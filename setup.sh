#!/bin/bash

# Clone the repository (optional, if not already done)
# git clone https://github.com/yourusername/yourrepo.git
# cd yourrepo

# Create and activate conda environment
conda create -n clms_api_advanced python=3.10 -y
source $(conda info --base)/etc/profile.d/conda.sh
conda activate clms_api_advanced

# Install required Python packages
conda install -y geopandas rasterio shapely requests fiona gdal pyogrio
