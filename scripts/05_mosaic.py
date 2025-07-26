"""
Summary:
--------
This script creates mosaics from downloaded CLMS product images for each product, date, and layer.
It groups images by date and layer, and if more than one image exists for a group, it merges them into a single mosaic using rasterio.
Mosaics are saved in a 'mosaic' subfolder for each product.
If only one image exists for a group, no mosaic is created for that group.

Code with comments:
-------------------
"""

import os
import glob
import rasterio
from rasterio.merge import merge
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
import re
from collections import defaultdict

# List of all possible layers to process
LAYERS = ["CLD", "FSCOG", "FSCTOC", "NDSI", "QCFLAGS", "QCOG", "QCTOC"]

def get_date_from_filename(filename):
    # Extracts date in format YYYYMMDD from filename like FSC_20230101T102754_S2B_T32TPS_V102_1
    match = re.search(r'_(\d{8})T', filename)
    return match.group(1) if match else None

def get_layer_from_filename(filename):
    # Match layer at the end before .tif, case-insensitive
    for layer in LAYERS:
        if filename.lower().endswith(f"_{layer.lower()}.tif"):
            return layer
    return None

def mosaic_images(image_list, output_path):
    # Open all images to be mosaicked
    src_files_to_mosaic = [rasterio.open(fp) for fp in image_list]
    # Merge images into a single mosaic
    mosaic, out_trans = merge(src_files_to_mosaic)
    # Copy metadata from the first image and update for the mosaic
    out_meta = src_files_to_mosaic[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans
    })
    # Write the mosaic to disk
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(mosaic)
    # Close all opened files
    for src in src_files_to_mosaic:
        src.close()

if __name__ == "__main__":
    if config.mosaic_output:
        print("Starting mosaicking process...")
        for product_type in config.clms_product:
            print(f"\nProcessing product: {product_type}")
            product_dir = os.path.join(os.path.dirname(config.__file__), "data/clms_data/original", product_type)
            mosaic_dir = os.path.join(product_dir, "mosaic")
            os.makedirs(mosaic_dir, exist_ok=True)

            # Find all subfolders (one per tile/date)
            subfolders = [f for f in os.listdir(product_dir) if os.path.isdir(os.path.join(product_dir, f)) and f != "mosaic"]
            # {date: {layer: [file1, file2, ...]}}
            date_layer_dict = defaultdict(lambda: defaultdict(list))

            # Group tifs by date and layer
            for subfolder in subfolders:
                date = get_date_from_filename(subfolder)
                if not date:
                    print(f"  Skipping folder (no date found): {subfolder}")
                    continue
                tif_files = glob.glob(os.path.join(product_dir, subfolder, "*.tif"))
                for tif in tif_files:
                    layer = get_layer_from_filename(os.path.basename(tif))
                    if layer:
                        date_layer_dict[date][layer].append(tif)
                    else:
                        print(f"    Skipping file (unknown layer): {tif}")

            # For each date and layer, create a mosaic if more than one image exists
            for date, layer_dict in date_layer_dict.items():
                for layer, files in layer_dict.items():
                    if len(files) > 1:
                        output_path = os.path.join(mosaic_dir, f"mosaic_{product_type}_{layer}_{date}.tif")
                        print(f"  Mosaicing {len(files)} images for date {date}, layer {layer} into {output_path}")
                        mosaic_images(files, output_path)
                        print(f"    Mosaic written: {output_path}")
                    elif len(files) == 1:
                        print(f"  Only one image for date {date}, layer {layer}, skipping mosaicing.")
        print("\nMosaicking process finished.")
    else:
        print("Mosaicking is disabled in config (mosaic_output is False).")