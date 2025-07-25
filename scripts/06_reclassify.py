"""
Summary:
--------
This script reclassifies selected CLMS product layers (FSCTOC, FSCOG, NDSI) by converting cloud/shadow (205) and nodata (255) values to a unified NA value (-9999).
It processes both individual images and mosaics, saving reclassified outputs with a "_reclass" suffix in the filename.
Other layers are simply copied without modification.

Code with comments:
-------------------
"""

import os
import glob
import numpy as np
import rasterio
import sys
sys.path.append('../')
import config

LAYERS_TO_RECLASSIFY = ["FSCTOC", "FSCOG", "NDSI"]  # Layers to be reclassified
NODATA_VALUE = -9999  # Value used for NA/nodata in output
RECLASS_SUFFIX = "_reclass"  # Suffix for reclassified files

def reclassify_array(arr):
    # Convert input array to float32 and set cloud/shadow and nodata to NODATA_VALUE
    arr = arr.astype(np.float32)
    arr[arr == 205] = NODATA_VALUE  # Cloud or cloud shadow
    arr[arr == 255] = NODATA_VALUE  # No data
    return arr

def process_folder(product_type, in_dir, out_dir):
    # Process all subfolders (tiles/dates) for a given product type
    for subfolder in os.listdir(in_dir):
        subfolder_path = os.path.join(in_dir, subfolder)
        if not os.path.isdir(subfolder_path) or subfolder == "mosaic":
            continue
        out_subfolder = os.path.join(out_dir, subfolder)
        os.makedirs(out_subfolder, exist_ok=True)
        tif_files = glob.glob(os.path.join(subfolder_path, "*.tif"))
        for tif_path in tif_files:
            layer = os.path.basename(tif_path).split("_")[-1].replace(".tif", "").upper()
            base_name = os.path.basename(tif_path)
            # Add _reclass suffix for reclassified layers
            if layer in LAYERS_TO_RECLASSIFY:
                out_name = base_name.replace(f"_{layer}.tif", f"_{layer}{RECLASS_SUFFIX}.tif")
            else:
                out_name = base_name
            out_path = os.path.join(out_subfolder, out_name)
            if layer in LAYERS_TO_RECLASSIFY:
                with rasterio.open(tif_path) as src:
                    arr = src.read(1)
                    arr_reclass = reclassify_array(arr)
                    meta = src.meta.copy()
                    meta.update(dtype='float32', nodata=NODATA_VALUE)
                    with rasterio.open(out_path, "w", **meta) as dst:
                        dst.write(arr_reclass, 1)
                print(f"Reclassified {tif_path} -> {out_path}")
            else:
                # Just copy the file if not reclassified
                with rasterio.open(tif_path) as src:
                    meta = src.meta.copy()
                    data = src.read()
                    with rasterio.open(out_path, "w", **meta) as dst:
                        dst.write(data)
                print(f"Copied (no reclass): {tif_path} -> {out_path}")

def process_mosaic(product_type, in_dir, out_dir):
    # Process mosaic images for a given product type
    mosaic_in_dir = os.path.join(in_dir, "mosaic")
    mosaic_out_dir = os.path.join(out_dir, "mosaic")
    os.makedirs(mosaic_out_dir, exist_ok=True)
    tif_files = glob.glob(os.path.join(mosaic_in_dir, "*.tif"))
    for tif_path in tif_files:
        # e.g. mosaic_FSC_FSCTOC_20230101.tif
        parts = os.path.basename(tif_path).split("_")
        if len(parts) < 4:
            print(f"Warning: Unexpected mosaic filename format: {tif_path}")
            continue
        layer = parts[2].upper()
        base_name = os.path.basename(tif_path)
        # Add _reclass suffix for reclassified layers
        if layer in LAYERS_TO_RECLASSIFY:
            out_name = base_name.replace(f"_{layer}_", f"_{layer}{RECLASS_SUFFIX}_")
        else:
            out_name = base_name
        out_path = os.path.join(mosaic_out_dir, out_name)
        if layer in LAYERS_TO_RECLASSIFY:
            with rasterio.open(tif_path) as src:
                arr = src.read(1)
                arr_reclass = reclassify_array(arr)
                meta = src.meta.copy()
                meta.update(dtype='float32', nodata=NODATA_VALUE)
                with rasterio.open(out_path, "w", **meta) as dst:
                    dst.write(arr_reclass, 1)
            print(f"Reclassified mosaic {tif_path} -> {out_path}")
        else:
            # Just copy the file if not reclassified
            with rasterio.open(tif_path) as src:
                meta = src.meta.copy()
                data = src.read()
                with rasterio.open(out_path, "w", **meta) as dst:
                    dst.write(data)
            print(f"Copied mosaic (no reclass): {tif_path} -> {out_path}")

if __name__ == "__main__":
    # Only run if reclassification is enabled in config
    if config.reclassify:
        for product_type in config.clms_product:
            # Process original (unmosaiced)
            in_dir = os.path.join(config.output_path_original, product_type)
            out_dir = os.path.join(config.output_path_processed, "reclassified", product_type)
            process_folder(product_type, in_dir, out_dir)
            # Process mosaiced
            process_mosaic(product_type, in_dir, out_dir)
    else:
        print("Reclassification is disabled in config (reclassify is set to False).")