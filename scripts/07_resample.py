def get_raster_folder_name(raster_entry):
    return os.path.splitext(raster_entry["name"])[0]


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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

def resample_raster(input_path, reference_path, output_path, resampling_method=Resampling.nearest, crs_str=None):
    # Open the reference raster to get its grid and projection
    with rasterio.open(reference_path) as ref:
        ref_crs = ref.crs
        ref_transform = ref.transform
        ref_width = ref.width
        ref_height = ref.height
        ref_nodata = ref.nodata if ref.nodata is not None else -9999 
        ref_dtype = ref.dtypes[0]

    # Open the input raster to be resampled
    with rasterio.open(input_path) as src:
        # Extract layer name robustly: if reclassify is enabled and filename ends with _reclass.tif, use second-to-last part; else last part
        base = os.path.basename(input_path).replace(".tif", "")
        parts = base.split("_")
        if hasattr(config, "reclassify") and config.reclassify and base.endswith("_reclass") and len(parts) > 1:
            layer_name = parts[-2].upper()
        else:
            layer_name = parts[-1].upper()

        # Prepare output raster metadata (settings)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': crs_str if crs_str else ref_crs,  # Set output projection to config CRS string if provided
            'transform': ref_transform,     # Set output grid to match reference
            'width': ref_width,             # Set output width to match reference
            'height': ref_height,           # Set output height to match reference
            'nodata': ref_nodata,           # Use reference nodata value
            'dtype': ref_dtype              # Store output as 32-bit float
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
    categorical = {"CLD", "QCFLAGS", "QCOG", "QCTOC","QC","SSC","QCSSC","WSM","QCWSM","QC","QCFLAGS"}
    if layer.upper() in categorical:
        return Resampling.nearest
    else:
        return Resampling.bilinear

def add_resampled_suffix(filename):
    """
    If the filename ends with '_reclass.tif', add '_resampled' before .tif (result: _reclass_resampled.tif).
    Otherwise, just add '_resampled' before .tif.
    """
    if filename.lower().endswith('_reclass.tif'):
        return filename[:-4] + '_resampled.tif'
    elif filename.lower().endswith('.tif'):
        return filename[:-4] + '_resampled.tif'
    return filename + '_resampled'

def process_folder(product_type, in_dir, out_dir, reference_raster, crs_str=None):
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
            base = os.path.basename(tif_path).replace(".tif", "")
            parts = base.split("_")
            if hasattr(config, "reclassify") and config.reclassify and base.endswith("_reclass") and len(parts) > 1:
                layer = parts[-2].upper()
            else:
                layer = parts[-1].upper()
            base_name = os.path.basename(tif_path)
            out_name = add_resampled_suffix(base_name)
            out_path = os.path.join(out_subfolder, out_name)
            resampling_method = get_resampling_method(layer)
            print(f"Resampling {tif_path} -> {out_path} (method: {resampling_method.name})")
            resample_raster(tif_path, reference_raster, out_path, resampling_method, crs_str=crs_str)

def process_mosaic(product_type, in_dir, out_dir, reference_raster, crs_str=None):
    # Process mosaic images for a given product type
    mosaic_in_dir = os.path.join(in_dir, "mosaic")
    mosaic_out_dir = os.path.join(out_dir, "mosaic")
    os.makedirs(mosaic_out_dir, exist_ok=True)
    tif_files = glob.glob(os.path.join(mosaic_in_dir, "*.tif"))
    for tif_path in tif_files:
        base = os.path.basename(tif_path).replace(".tif", "")
        parts = base.split("_")
        # For mosaic files, layer name is always the third part (e.g., mosaic_WDS_SSC_reclass_20230705.tif)
        if len(parts) > 2:
            layer = parts[2].upper()
        else:
            layer = parts[-1].upper()
        base_name = os.path.basename(tif_path)
        out_name = add_resampled_suffix(base_name)
        out_path = os.path.join(mosaic_out_dir, out_name)
        resampling_method = get_resampling_method(layer)
        print(f"Resampling mosaic {tif_path} -> {out_path} (method: {resampling_method.name})")
        resample_raster(tif_path, reference_raster, out_path, resampling_method, crs_str=crs_str)

if __name__ == "__main__":
    # Only run if resampling/cropping is enabled in config
    if hasattr(config, "crop_resample") and config.crop_resample:
        reference_rasters = config.reference_rasters
        # Use reclassified rasters if reclassify is True, otherwise use original rasters
        if hasattr(config, "reclassify") and config.reclassify:
            base_in_dir = os.path.join(os.path.dirname(config.__file__), "data/clms_data/processed", "reclassified")
            use_reclass_suffix = True
        else:
            base_in_dir = os.path.join(os.path.dirname(config.__file__), "data/clms_data/original")
            use_reclass_suffix = False
        base_out_dir = os.path.join(os.path.dirname(config.__file__), "data/clms_data/processed", "resampled")
        os.makedirs(base_out_dir, exist_ok=True)

        for raster_entry in reference_rasters:
            raster_folder = get_raster_folder_name(raster_entry)
            reference_raster = config.get_reference_raster_path(raster_entry)
            crs_str = raster_entry["crs"]
            print(f"\n=== Processing reference raster: {raster_entry['name']} (folder: {raster_folder}) ===")
            out_dir_raster = os.path.join(base_out_dir, raster_folder)
            os.makedirs(out_dir_raster, exist_ok=True)
            for product_type in config.clms_product:
                in_dir = os.path.join(base_in_dir, raster_folder, product_type)
                if not os.path.exists(in_dir) or not any(os.scandir(in_dir)):
                    in_dir = os.path.join(os.path.dirname(config.__file__), "data/clms_data/original", raster_folder, product_type)
                    use_reclass_suffix = False
                out_dir = os.path.join(out_dir_raster, product_type)
                process_folder(product_type, in_dir, out_dir, reference_raster, crs_str=crs_str)
                process_mosaic(product_type, in_dir, out_dir, reference_raster, crs_str=crs_str)
    else:
        print("Resampling and cropping is disabled in config (crop_resample is False).")