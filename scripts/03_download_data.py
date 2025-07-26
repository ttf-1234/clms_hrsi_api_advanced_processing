"""
Summary:
--------
This script manages the download (or query) of Copernicus Land Monitoring Service (CLMS) snow products for a set of Sentinel-2 tiles and a specified date range.
It ensures credentials are available, validates configuration, and calls the official CLMS HRSI API client (CLMS_downloader.py) for each tile and product type.
Downloaded data is organized by product and tile, and result files are renamed for clarity.

Source of the official CLMS downloader: https://github.com/eea/clms-hrsi-api-client-python

Code with comments:
-------------------
"""

import sys
import os
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config



# --- Ensure clms_data directory exists ---
clms_data_dir = os.path.join(os.path.dirname(config.__file__), "data/clms_data")
os.makedirs(clms_data_dir, exist_ok=True)

# --- Ensure credentials file exists ---
credentials_path = os.path.join(clms_data_dir, "credentials.txt")
if not os.path.exists(credentials_path):
    with open(credentials_path, "w") as f:
        f.write(f"{config.clms_username}:{config.clms_password}\n")
    print(f"Created credentials file at {credentials_path}")
else:
    print(f"Credentials file already exists at {credentials_path}")
    # Check file integrity
    with open(credentials_path, "r") as f:
        line = f.readline().strip()
    if ':' not in line or not all(line.split(':')):
        print(f"Credentials file at {credentials_path} is incomplete or malformed. Recreating...")
        with open(credentials_path, "w") as f:
            f.write(f"{config.clms_username}:{config.clms_password}\n")

# Allowed Copernicus snow products (WMS services)
ALLOWED_PRODUCTS = ["FSC", "PSA", "SWS", "WDS", "GFSC"]
ALLOWED_QUERY_TYPES = ["query", "download", "query_and_download"]

def is_valid_date(date_str):
    # Check for format YYYY-MM-DDTHH:MM:SSZ
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    return bool(re.match(pattern, date_str))

# Read tile names from the txt file produced by 02_determine_tile.py
if not os.path.exists(config.tile_txt_path):
    print(f"Tile txt file not found: {config.tile_txt_path}")
    sys.exit(1)

with open(config.tile_txt_path, 'r') as f:
    tile_names = [line.strip() for line in f if line.strip()]

if not tile_names:
    print("No tile names found in the txt file.")
    sys.exit(1)

start_date = config.start_date
end_date = config.end_date
product_types = config.clms_product
output_path = config.output_path_original
query_type = config.clms_query_type

# Check if all product_types are valid
invalid_products = [p for p in product_types if p not in ALLOWED_PRODUCTS]
if invalid_products:
    print(f"Invalid product types found: {invalid_products}")
    print(f"Allowed products are: {ALLOWED_PRODUCTS}")
    sys.exit(1)

# Check date formats
if not is_valid_date(start_date):
    print(f"Start date format invalid: {start_date}")
    print("Expected format: YYYY-MM-DDTHH:MM:SSZ")
    sys.exit(1)
if not is_valid_date(end_date):
    print(f"End date format invalid: {end_date}")
    print("Expected format: YYYY-MM-DDTHH:MM:SSZ")
    sys.exit(1)

# Check query type
if query_type not in ALLOWED_QUERY_TYPES:
    print(f"Invalid query type: {query_type}")
    print(f"Allowed query types are: {ALLOWED_QUERY_TYPES}")
    sys.exit(1)

# Loop over all tiles and product types, and run the official CLMS downloader for each
for tile in tile_names:
    for product_type in product_types:
        # Ensure product-specific output directory exists
        product_output_dir = os.path.join(config.output_path_original, product_type)
        os.makedirs(product_output_dir, exist_ok=True)

        # Build the command to run the CLMS_downloader.py script
        clms_downloader_path = os.path.join(os.path.dirname(__file__), "CLMS_downloader.py")
        cmd = (
            f"python {clms_downloader_path} "
            f"-{query_type} "
            f"-productIdentifier {tile} "
            f"-productType {product_type} "
            f"-obsDateMin {start_date} "
            f"-obsDateMax {end_date} "
            f"-hrsi_credentials {credentials_path} "
            f"{product_output_dir}"
        )
        print(f"Running: {cmd}")
        os.system(cmd)

        # Rename result_file.txt if it exists, to include tile and product type for clarity
        result_file = os.path.join(product_output_dir, "result_file.txt")
        new_result_file = os.path.join(product_output_dir, f"result_file_{tile}_{product_type}.txt")
        if os.path.exists(result_file):
            os.rename(result_file, new_result_file)
            print(f"Renamed {result_file} to {new_result_file}")
        else:
            print(f"Warning: {result_file} not found after download.")

# Source of the official CLMS downloader: https://github.com/eea/clms-hrsi-api-client-python
