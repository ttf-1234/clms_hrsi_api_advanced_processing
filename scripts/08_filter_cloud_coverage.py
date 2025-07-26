"""
Summary:
--------
This script filters processed (or original) CLMS images for cloud coverage inside the area of interest (AOI).
It uses the FSCOG layer to determine cloud pixels (205 for original, -9999 for reclassified).
Only images with a cloud coverage percentage below the threshold specified in config.cc_threshold are kept.
The filtered images are saved under processed/cc_filtered, preserving the directory structure.
This filtering is only performed if crop_resample and filter_cc are enabled in the config.
If no mosaics are found, non-mosaic images are used.

Code with comments:
-------------------
"""

import os
import glob
import rasterio
import numpy as np
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

def get_cloud_mask(arr, use_reclassify):
    """
    Returns a boolean mask where True indicates cloud or cloud shadow.
    For FSCOG: 205 = cloud/shadow (original), -9999 = cloud/shadow (reclassified).
    """
    if use_reclassify:
        return arr == -9999
    else:
        return arr == 205

def filter_by_cloud_coverage(input_dir, output_dir, cc_threshold, use_reclassify):
    os.makedirs(output_dir, exist_ok=True)
    for subfolder in os.listdir(input_dir):
        subfolder_path = os.path.join(input_dir, subfolder)
        if not os.path.isdir(subfolder_path) or subfolder == "mosaic":
            continue
        out_subfolder = os.path.join(output_dir, subfolder)
        os.makedirs(out_subfolder, exist_ok=True)
        tif_files = glob.glob(os.path.join(subfolder_path, "*.tif"))
        for tif_path in tif_files:
            # Always use the corresponding FSCOG file for cloud masking
            base_parts = os.path.basename(tif_path).split("_")
            base_parts[-1] = "FSCOG.tif"
            fscog_filename = "_".join(base_parts)
            fscog_path = os.path.join(subfolder_path, fscog_filename)
            if not os.path.exists(fscog_path):
                print(f"FSCOG file not found for {tif_path}, skipping cloud filtering.")
                continue
            with rasterio.open(fscog_path) as fscog_src:
                fscog_arr = fscog_src.read(1)
                cloud_mask = get_cloud_mask(fscog_arr, use_reclassify)
                valid_mask = (fscog_arr != -9999) if use_reclassify else (fscog_arr != 255)
                total_pixels = np.sum(valid_mask)
                cloud_pixels = np.sum(cloud_mask & valid_mask)
                cc_fraction = cloud_pixels / total_pixels if total_pixels > 0 else 0
            with rasterio.open(tif_path) as src:
                arr = src.read(1)
                if cc_fraction <= cc_threshold:
                    out_path = os.path.join(out_subfolder, os.path.basename(tif_path))
                    with rasterio.open(out_path, "w", **src.meta) as dst:
                        dst.write(arr, 1)
                    print(f"Kept {tif_path} (cloud fraction: {cc_fraction:.2%})")
                else:
                    print(f"Filtered out {tif_path} (cloud fraction: {cc_fraction:.2%})")

if __name__ == "__main__":
    # Only run if crop_resample and filter_cc are enabled
    if getattr(config, "crop_resample", False) and getattr(config, "filter_cc", False):
        use_reclassify = getattr(config, "reclassify", False)

        cc_threshold = config.cc_threshold
        base_in_dir = os.path.join(os.path.dirname(config.__file__), "data/clms_data/processed", "resampled")
        base_out_dir = os.path.join(os.path.dirname(config.__file__), "data/clms_data/processed", "cc_filtered")

        for product_type in config.clms_product:
            # Prefer mosaics if available, otherwise use non-mosaic
            mosaic_dir = os.path.join(base_in_dir, product_type, "mosaic")
            if os.path.exists(mosaic_dir) and any(glob.glob(os.path.join(mosaic_dir, "*.tif"))):
                in_dir = mosaic_dir
                out_dir = os.path.join(base_out_dir, product_type, "mosaic")
                print(f"Filtering cloud coverage in mosaiced resampled images for {product_type}...")
                filter_by_cloud_coverage(in_dir, out_dir, cc_threshold, use_reclassify)
            else:
                in_dir = os.path.join(base_in_dir, product_type)
                out_dir = os.path.join(base_out_dir, product_type)
                print(f"No mosaics found, filtering resampled images for {product_type}...")
                filter_by_cloud_coverage(in_dir, out_dir, cc_threshold, use_reclassify)
    else:
        print("Cloud coverage filtering is only available if crop_resample and filter_cc are enabled in the config.")