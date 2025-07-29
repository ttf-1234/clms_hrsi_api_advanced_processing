import os
import glob
import rasterio
from rasterio.merge import merge
import re
from collections import defaultdict

class MosaicBuilder:
    LAYERS = ["CLD", "FSCOG", "FSCTOC", "NDSI", "QCFLAGS", "QCOG", "QCTOC","PSA","QC","SSC","QCSSC","WSM","QCWSM","AT","GF"]

    def __init__(self, config):
        self.config = config

    def get_date_from_filename(self, filename):
        match = re.search(r'_(\d{8})(?:T|-)', filename)
        return match.group(1) if match else None

    def get_layer_from_filename(self, filename):
        for layer in self.LAYERS:
            if filename.lower().endswith(f"_{layer.lower()}.tif"):
                return layer
        return None

    def mosaic_images(self, image_list, output_path):
        src_files_to_mosaic = [rasterio.open(fp) for fp in image_list]
        mosaic, out_trans = merge(src_files_to_mosaic)
        out_meta = src_files_to_mosaic[0].meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans
        })
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(mosaic)
        for src in src_files_to_mosaic:
            src.close()

    def build_mosaic(self):
        if not getattr(self.config, "mosaic_output", False):
            print("Mosaicking is disabled in the configuration. Skipping mosaic step.")
            return

        project_root = os.getcwd()  # Use main project directory
        input_base = os.path.join(project_root, self.config.output_path_original)

        for raster_entry in self.config.reference_rasters:
            raster_folder = os.path.splitext(raster_entry["name"])[0]
            print(f"\n=== Processing reference raster: {raster_entry['name']} (folder: {raster_folder}) ===")
            for product_type in self.config.clms_product:
                print(f"  Processing product: {product_type}")
                product_dir = os.path.join(input_base, raster_folder, product_type)
                mosaic_dir = os.path.join(product_dir, "mosaic")
                os.makedirs(mosaic_dir, exist_ok=True)

                if not os.path.isdir(product_dir):
                    print(f"    Product directory not found: {product_dir}")
                    continue

                subfolders = [f for f in os.listdir(product_dir) if os.path.isdir(os.path.join(product_dir, f)) and f != "mosaic"]
                date_layer_dict = defaultdict(lambda: defaultdict(list))

                for subfolder in subfolders:
                    date = self.get_date_from_filename(subfolder)
                    if not date:
                        print(f"    Skipping folder (no date found): {subfolder}")
                        continue
                    tif_files = glob.glob(os.path.join(product_dir, subfolder, "*.tif"))
                    for tif in tif_files:
                        layer = self.get_layer_from_filename(os.path.basename(tif))
                        if layer:
                            date_layer_dict[date][layer].append(tif)
                        else:
                            print(f"      Skipping file (unknown layer): {tif}")

                for date, layer_dict in date_layer_dict.items():
                    for layer, files in layer_dict.items():
                        if len(files) > 1:
                            output_path = os.path.join(mosaic_dir, f"mosaic_{product_type}_{layer}_{date}.tif")
                            print(f"    Mosaicing {len(files)} images for date {date}, layer {layer} into {output_path}")
                            self.mosaic_images(files, output_path)
                            print(f"      Mosaic written: {output_path}")
                        elif len(files) == 1:
                            print(f"    Only one image for date {date}, layer {layer}, skipping mosaicing.")
        print("\nMosaicking process finished.")
