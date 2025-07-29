import os
import glob
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np

NODATA_VALUE = -9999

class Resampler:
    def __init__(self, config):
        self.config = config

    def resample_raster(self, input_path, reference_path, output_path, resampling_method=Resampling.nearest, crs_str=None):
        with rasterio.open(reference_path) as ref:
            ref_crs = ref.crs
            ref_transform = ref.transform
            ref_width = ref.width
            ref_height = ref.height
            ref_nodata = ref.nodata if ref.nodata is not None else NODATA_VALUE
            ref_dtype = ref.dtypes[0]
        with rasterio.open(input_path) as src:
            base = os.path.basename(input_path).replace(".tif", "")
            parts = base.split("_")
            if hasattr(self.config, "reclassify") and self.config.reclassify and base.endswith("_reclass") and len(parts) > 1:
                layer_name = parts[-2].upper()
            else:
                layer_name = parts[-1].upper()
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': crs_str if crs_str else ref_crs,
                'transform': ref_transform,
                'width': ref_width,
                'height': ref_height,
                'nodata': ref_nodata,
                'dtype': ref_dtype
            })
            with rasterio.open(output_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=ref_transform,
                        dst_crs=ref_crs,
                        resampling=resampling_method
                    )

    def get_resampling_method(self, layer):
        categorical = {"CLD", "QCFLAGS", "QCOG", "QCTOC","QC","SSC","QCSSC","WSM","QCWSM","QC","QCFLAGS"}
        if layer.upper() in categorical:
            return Resampling.nearest
        else:
            return Resampling.bilinear

    def add_resampled_suffix(self, filename):
        if filename.lower().endswith('_reclass.tif'):
            return filename[:-4] + '_resampled.tif'
        elif filename.lower().endswith('.tif'):
            return filename[:-4] + '_resampled.tif'
        return filename + '_resampled'

    def process_folder(self, product_type, in_dir, out_dir, reference_raster, crs_str=None):
        print(in_dir)
        for subfolder in os.listdir(in_dir):
            subfolder_path = os.path.join(in_dir, subfolder)
            print(subfolder_path)
            if not os.path.isdir(subfolder_path) or subfolder == "mosaic":
                continue
            out_subfolder = os.path.join(out_dir, subfolder)
            os.makedirs(out_subfolder, exist_ok=True)
            tif_files = glob.glob(os.path.join(subfolder_path, "*.tif"))
            for tif_path in tif_files:
                base = os.path.basename(tif_path).replace(".tif", "")
                parts = base.split("_")
                if hasattr(self.config, "reclassify") and self.config.reclassify and base.endswith("_reclass") and len(parts) > 1:
                    layer = parts[-2].upper()
                else:
                    layer = parts[-1].upper()
                base_name = os.path.basename(tif_path)
                out_name = self.add_resampled_suffix(base_name)
                out_path = os.path.join(out_subfolder, out_name)
                resampling_method = self.get_resampling_method(layer)
                print(f"Resampling {tif_path} -> {out_path} (method: {resampling_method.name})")
                self.resample_raster(tif_path, reference_raster, out_path, resampling_method, crs_str=crs_str)

    def process_mosaic(self, product_type, in_dir, out_dir, reference_raster, crs_str=None):
        mosaic_in_dir = os.path.join(in_dir, "mosaic")
        mosaic_out_dir = os.path.join(out_dir, "mosaic")
        os.makedirs(mosaic_out_dir, exist_ok=True)
        tif_files = glob.glob(os.path.join(mosaic_in_dir, "*.tif"))
        for tif_path in tif_files:
            base = os.path.basename(tif_path).replace(".tif", "")
            parts = base.split("_")
            if hasattr(self.config, "reclassify") and self.config.reclassify and base.endswith("_reclass") and len(parts) > 1:
                layer = parts[-2].upper()
            else:
                layer = parts[-1].upper()
            base_name = os.path.basename(tif_path)
            out_name = self.add_resampled_suffix(base_name)
            out_path = os.path.join(mosaic_out_dir, out_name)
            resampling_method = self.get_resampling_method(layer)
            print(f"Resampling mosaic {tif_path} -> {out_path} (method: {resampling_method.name})")
            self.resample_raster(tif_path, reference_raster, out_path, resampling_method, crs_str=crs_str)

    def resample(self):
        if not getattr(self.config, "crop_resample", False):
            print("Resampling is disabled in the configuration. Skipping resample step.")
            return
        print("Starting resampling process...")
        project_root = os.getcwd()
        for raster_entry in self.config.reference_rasters:
            raster_folder = os.path.splitext(raster_entry["name"])[0]
            reference_raster = os.path.join(self.config.reference_raster_dir, raster_entry["name"])
            crs_str = raster_entry["crs"]
            for product_type in self.config.clms_product:
                # Output always goes to processed
                out_base_dir = os.path.join(project_root, "data/clms_data/processed", raster_folder, product_type)
                out_dir = os.path.join(out_base_dir, "resampled")
                os.makedirs(out_dir, exist_ok=True)
                os.makedirs(os.path.join(out_dir, "mosaic"), exist_ok=True)
                # Input depends on reclassify
                if getattr(self.config, "reclassify", False):
                    in_dir = os.path.join(project_root, "data/clms_data/processed", raster_folder, product_type, "reclassified")
                else:
                    in_dir = os.path.join(project_root, "data/clms_data/original", raster_folder, product_type)
                self.process_folder(product_type, in_dir, out_dir, reference_raster, crs_str=crs_str)
                self.process_mosaic(product_type, in_dir, out_dir, reference_raster, crs_str=crs_str)
        print("Resampling process finished.")
