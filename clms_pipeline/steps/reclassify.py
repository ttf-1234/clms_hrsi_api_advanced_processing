import os
import glob
import numpy as np
import rasterio

PRODUCT_LAYERS_TO_RECLASSIFY = {
    "FSC": ["FSCTOC", "FSCOG", "NDSI"],
    "PSA": ["PSA"],
    "WDS": ["SSC"],
    "SWS": ["WSM"],
    "GFSC": ["GF"]
}
NODATA_VALUE = -9999
RECLASS_SUFFIX = "_reclass"

class Reclassifier:
    def __init__(self, config):
        self.config = config

    def reclassify_array(self, arr):
        arr = arr.astype(np.float32)
        arr[arr == 205] = NODATA_VALUE
        arr[arr == 255] = NODATA_VALUE
        return arr

    def process_folder(self, product_type, in_dir, out_dir):
        for subfolder in os.listdir(in_dir):
            subfolder_path = os.path.join(in_dir, subfolder)
            if not os.path.isdir(subfolder_path) or subfolder == "mosaic":
                continue
            out_subfolder = os.path.join(out_dir, "reclassified", subfolder)
            os.makedirs(out_subfolder, exist_ok=True)
            tif_files = glob.glob(os.path.join(subfolder_path, "*.tif"))
            for tif_path in tif_files:
                layer = os.path.basename(tif_path).split("_")[-1].replace(".tif", "").upper()
                base_name = os.path.basename(tif_path)
                if layer in PRODUCT_LAYERS_TO_RECLASSIFY.get(product_type, []):
                    if base_name.lower().endswith('.tif'):
                        out_name = base_name[:-4] + f'{RECLASS_SUFFIX}.tif'
                    else:
                        out_name = base_name + f'{RECLASS_SUFFIX}'
                else:
                    out_name = base_name
                out_path = os.path.join(out_subfolder, out_name)
                if layer in PRODUCT_LAYERS_TO_RECLASSIFY.get(product_type, []):
                    with rasterio.open(tif_path) as src:
                        arr = src.read(1)
                        arr_reclass = self.reclassify_array(arr)
                        meta = src.meta.copy()
                        meta.update(dtype='float32', nodata=NODATA_VALUE)
                        with rasterio.open(out_path, "w", **meta) as dst:
                            dst.write(arr_reclass, 1)
                    print(f"Reclassified {tif_path} -> {out_path}")
                else:
                    with rasterio.open(tif_path) as src:
                        meta = src.meta.copy()
                        data = src.read()
                        with rasterio.open(out_path, "w", **meta) as dst:
                            dst.write(data)
                    print(f"Copied (no reclass): {tif_path} -> {out_path}")

    def process_mosaic(self, product_type, in_dir, out_dir):
        mosaic_in_dir = os.path.join(in_dir, "mosaic")
        mosaic_out_dir = os.path.join(out_dir, "reclassified", "mosaic")
        os.makedirs(mosaic_out_dir, exist_ok=True)
        tif_files = glob.glob(os.path.join(mosaic_in_dir, "*.tif"))
        for tif_path in tif_files:
            parts = os.path.basename(tif_path).split("_")
            if len(parts) < 4:
                print(f"Warning: Unexpected mosaic filename format: {tif_path}")
                continue
            layer = parts[2].upper()
            base_name = os.path.basename(tif_path)
            if layer in PRODUCT_LAYERS_TO_RECLASSIFY.get(product_type, []):
                if base_name.lower().endswith('.tif'):
                    out_name = base_name[:-4] + f'{RECLASS_SUFFIX}.tif'
                else:
                    out_name = base_name + f'{RECLASS_SUFFIX}'
            else:
                out_name = base_name
            out_path = os.path.join(mosaic_out_dir, out_name)
            if layer in PRODUCT_LAYERS_TO_RECLASSIFY.get(product_type, []):
                with rasterio.open(tif_path) as src:
                    arr = src.read(1)
                    arr_reclass = self.reclassify_array(arr)
                    meta = src.meta.copy()
                    meta.update(dtype='float32', nodata=NODATA_VALUE)
                    with rasterio.open(out_path, "w", **meta) as dst:
                        dst.write(arr_reclass, 1)
                print(f"Reclassified mosaic {tif_path} -> {out_path}")
            else:
                with rasterio.open(tif_path) as src:
                    meta = src.meta.copy()
                    data = src.read()
                    with rasterio.open(out_path, "w", **meta) as dst:
                        dst.write(data)
                print(f"Copied mosaic (no reclass): {tif_path} -> {out_path}")

    def reclassify(self):
        if not getattr(self.config, "reclassify", False):
            print("Reclassification is disabled in the configuration. Skipping reclassify step.")
            return
        print("Starting reclassification process...")
        project_root = os.getcwd()  # Use main project directory
        for raster_entry in self.config.reference_rasters:
            raster_folder = os.path.splitext(raster_entry["name"])[0]
            for product_type in self.config.clms_product:
                out_dir = os.path.join(project_root, self.config.output_path_processed, raster_folder, product_type)
                # Ensure subfolders exist
                os.makedirs(os.path.join(out_dir, "reclassified"), exist_ok=True)
                in_dir = os.path.join(project_root, self.config.output_path_original, raster_folder, product_type)
                self.process_folder(product_type, in_dir, out_dir)
                self.process_mosaic(product_type, in_dir, out_dir)
        print("Reclassification process finished.")
