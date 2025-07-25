"""
Summary:
--------
This script resamples all CLMS product rasters (and mosaics) to match a reference raster's grid, projection, and extent.
It supports both original and reclassified rasters, and adds appropriate suffixes to output filenames.
Resampled rasters are saved as float32 with -9999 as the NA/nodata value, ensuring compatibility with GIS software.

Code with comments:
-------------------
"""

import os
import glob
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
import sys
sys.path.append('../')
import config

def resample_raster(input_path, reference_path, output_path, resampling_method=Resampling.nearest):
    # Open the reference raster to get its grid and projection
    with rasterio.open(reference_path) as ref:
        ref_crs = ref.crs
        ref_transform = ref.transform
        ref_width = ref.width
        ref_height = ref.height

    # Open the input raster to be resampled
    with rasterio.open(input_path) as src:
        # Prepare output raster metadata (settings)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': ref_crs,                # Set output projection to match reference
            'transform': ref_transform,     # Set output grid to match reference
            'width': ref_width,             # Set output width to match reference
            'height': ref_height,           # Set output height to match reference
            'nodata': -9999.0,              # Use -9999 as the value for missing data
            'dtype': 'float32'              # Store output as 32-bit float
        })

        # Create the output raster file and write the resampled data
        with rasterio.open(output_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):  # Loop over all bands (usually 1)
                reproject(
                    source=rasterio.band(src, i),         # Input data
                    destination=rasterio.band(dst, i),    # Output location
                    src_transform=src.transform,          # Input grid
                    src_crs=src.crs,                      # Input projection
                    dst_transform=ref_transform,           # Output grid
                    dst_crs=ref_crs,                      # Output projection
                    resampling=resampling_method           # Resampling algorithm
                )

def get_resampling_method(layer):
    # Categorical layers should use nearest, continuous can use bilinear
    categorical = {"CLD", "QCFLAGS", "QCOG", "QCTOC"}
    if layer.upper() in categorical:
        return Resampling.nearest
    else:
        return Resampling.bilinear

def add_resampled_suffix(filename, use_reclass_suffix=False):
    """
    If use_reclass_suffix is True, keep the '_reclass' suffix if present and add '_resampled' before .tif.
    If False, just add '_resampled' before .tif.
    """
    if use_reclass_suffix:
        if filename.lower().endswith('_reclass.tif'):
            return filename[:-4] + '_resampled.tif'
        elif filename.lower().endswith('.tif'):
            return filename[:-4] + '_reclass_resampled.tif'
        return filename + '_reclass_resampled'
    else:
        if filename.lower().endswith('.tif'):
            return filename[:-4] + '_resampled.tif'
        return filename + '_resampled'

def process_folder(product_type, in_dir, out_dir, reference_raster, use_reclass_suffix):
    # Process all subfolders (tiles/dates) for a given product type
    for subfolder in os.listdir(in_dir):
        subfolder_path = os.path.join(in_dir, subfolder)
        # Skip if not a folder or if it's the 'mosaic' folder
        if not os.path.isdir(subfolder_path) or subfolder == "mosaic":
            continue
        out_subfolder = os.path.join(out_dir, subfolder)
        os.makedirs(out_subfolder, exist_ok=True)
        tif_files = glob.glob(os.path.join(subfolder_path, "*.tif"))
        for tif_path in tif_files:
            layer = os.path.basename(tif_path).split("_")[-1].replace(".tif", "").upper()
            base_name = os.path.basename(tif_path)
            out_name = add_resampled_suffix(base_name, use_reclass_suffix)
            out_path = os.path.join(out_subfolder, out_name)
            resampling_method = get_resampling_method(layer)
            print(f"Resampling {tif_path} -> {out_path} (method: {resampling_method.name})")
            resample_raster(tif_path, reference_raster, out_path, resampling_method)

def process_mosaic(product_type, in_dir, out_dir, reference_raster, use_reclass_suffix):
    # Process mosaic images for a given product type
    mosaic_in_dir = os.path.join(in_dir, "mosaic")
    mosaic_out_dir = os.path.join(out_dir, "mosaic")
    os.makedirs(mosaic_out_dir, exist_ok=True)
    tif_files = glob.glob(os.path.join(mosaic_in_dir, "*.tif"))
    for tif_path in tif_files:
        parts = os.path.basename(tif_path).split("_")
        if len(parts) < 4:
            print(f"Warning: Unexpected mosaic filename format: {tif_path}")
            continue
        layer = parts[2].upper()
        base_name = os.path.basename(tif_path)
        out_name = add_resampled_suffix(base_name, use_reclass_suffix)
        out_path = os.path.join(mosaic_out_dir, out_name)
        resampling_method = get_resampling_method(layer)
        print(f"Resampling mosaic {tif_path} -> {out_path} (method: {resampling_method.name})")
        resample_raster(tif_path, reference_raster, out_path, resampling_method)

if __name__ == "__main__":
    # Only run if resampling/cropping is enabled in config
    if hasattr(config, "crop_resample") and config.crop_resample:
        reference_raster = config.reference_raster_path
        # Use reclassified rasters if reclassify is True, otherwise use original rasters
        if hasattr(config, "reclassify") and config.reclassify:
            base_in_dir = os.path.join(config.output_path_processed, "reclassified")
            use_reclass_suffix = True
        else:
            base_in_dir = config.output_path_original
            use_reclass_suffix = False
        base_out_dir = os.path.join(config.output_path_processed, "resampled")
        os.makedirs(base_out_dir, exist_ok=True)

        for product_type in config.clms_product:
            in_dir = os.path.join(base_in_dir, product_type)
            # If reclassify is False and reclassified folder does not exist, use original folder
            if not os.path.exists(in_dir) or not any(os.scandir(in_dir)):
                in_dir = os.path.join(config.output_path_original, product_type)
                use_reclass_suffix = False
            out_dir = os.path.join(base_out_dir, product_type)
            process_folder(product_type, in_dir, out_dir, reference_raster, use_reclass_suffix)
            process_mosaic(product_type, in_dir, out_dir, reference_raster, use_reclass_suffix)
    else:
        print("Resampling and cropping is disabled in config (crop_resample is False).")