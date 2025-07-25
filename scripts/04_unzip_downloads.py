"""
Summary:
--------
This script unzips all .zip files in the original download directories for each CLMS product and deletes the zip files after extraction.
It ensures that all downloaded data is available in unzipped form for further processing.

Code with comments:
-------------------
"""

import os
import zipfile
import sys
sys.path.append('../')
import config

def unzip_and_cleanup(product_type):
    # Get the directory for the current product type
    product_dir = os.path.join(config.output_path_original, product_type)
    if not os.path.isdir(product_dir):
        print(f"Directory not found: {product_dir}")
        return

    # Loop through all files in the product directory
    for fname in os.listdir(product_dir):
        if fname.endswith(".zip"):
            zip_path = os.path.join(product_dir, fname)
            try:
                # Extract all contents of the zip file to the product directory
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(product_dir)
                print(f"Unzipped: {zip_path}")
                # Delete the zip file after extraction
                os.remove(zip_path)
                print(f"Deleted: {zip_path}")
            except Exception as e:
                print(f"Error processing {zip_path}: {e}")

if __name__ == "__main__":
    # Unzip and clean up for each product type listed in the config
    for product_type in config.clms_product:
        unzip_and_cleanup(product_type)

