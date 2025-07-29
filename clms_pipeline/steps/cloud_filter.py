import os
import glob
import rasterio
import numpy as np

class CloudFilter:
    def __init__(self, config):
        self.config = config

    def get_cloud_mask(self, arr, use_reclassify):
        if use_reclassify:
            return arr == -9999
        else:
            return arr == 205

    def filter_by_cloud_coverage(self, input_dir, output_dir, cc_threshold, use_reclassify, product_type):
        os.makedirs(output_dir, exist_ok=True)
        product_layer_map = {
            "FSC": "FSCOG",
            "PSA": "PSA",
            "WDS": "SSC",
            "SWS": "WSM",
            "GFSC": "GF"
        }
        layer_suffix = product_layer_map.get(product_type.upper(), None)
        if layer_suffix is None:
            print(f"Unknown product type: {product_type}. Skipping cloud filtering.")
            return
        for subfolder in os.listdir(input_dir):
            subfolder_path = os.path.join(input_dir, subfolder)
            if not os.path.isdir(subfolder_path) or subfolder == "mosaic":
                continue
            out_subfolder = os.path.join(output_dir, subfolder)
            os.makedirs(out_subfolder, exist_ok=True)
            tif_files = glob.glob(os.path.join(subfolder_path, "*.tif"))
            for tif_path in tif_files:
                base_parts = os.path.basename(tif_path).split("_")
                base_parts[-1] = f"{layer_suffix}.tif"
                layer_filename = "_".join(base_parts)
                layer_path = os.path.join(subfolder_path, layer_filename)
                if not os.path.exists(layer_path):
                    print(f"Cloud mask layer file not found for {tif_path} (expected: {layer_filename}), skipping cloud filtering.")
                    continue
                with rasterio.open(layer_path) as mask_src:
                    mask_arr = mask_src.read(1)
                    cloud_mask = self.get_cloud_mask(mask_arr, use_reclassify)
                    valid_mask = (mask_arr != -9999) if use_reclassify else (mask_arr != 255)
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

    def filter_clouds(self):
        if not (getattr(self.config, "crop_resample", False) and getattr(self.config, "filter_cc", False)):
            print("Cloud coverage filtering is only available if crop_resample and filter_cc are enabled in the config.")
            return
        print("Starting cloud coverage filtering...")
        use_reclassify = getattr(self.config, "reclassify", False)
        cc_threshold = self.config.cc_threshold
        base_in_dir = os.path.join(os.getcwd(), "data/clms_data/processed", "resampled")
        base_out_dir = os.path.join(os.getcwd(), "data/clms_data/processed", "cc_filtered")

        for raster_entry in self.config.reference_rasters:
            raster_folder = os.path.splitext(raster_entry["name"])[0]
            for product_type in self.config.clms_product:
                # Ensure output subfolders exist
                os.makedirs(os.path.join(base_out_dir, raster_folder, product_type), exist_ok=True)
                os.makedirs(os.path.join(base_out_dir, raster_folder, product_type, "mosaic"), exist_ok=True)

                mosaic_dir = os.path.join(base_in_dir, raster_folder, product_type, "mosaic")
                if os.path.exists(mosaic_dir) and any(glob.glob(os.path.join(mosaic_dir, "*.tif"))):
                    in_dir = mosaic_dir
                    out_dir = os.path.join(base_out_dir, raster_folder, product_type, "mosaic")
                    print(f"Filtering cloud coverage in mosaiced resampled images for {raster_folder} / {product_type}...")
                    self.filter_by_cloud_coverage(in_dir, out_dir, cc_threshold, use_reclassify, product_type)
                else:
                    in_dir = os.path.join(base_in_dir, raster_folder, product_type)
                    out_dir = os.path.join(base_out_dir, raster_folder, product_type)
                    print(f"No mosaics found, filtering resampled images for {raster_folder} / {product_type}...")
                    self.filter_by_cloud_coverage(in_dir, out_dir, cc_threshold, use_reclassify, product_type)
        print("Cloud coverage filtering finished.")
