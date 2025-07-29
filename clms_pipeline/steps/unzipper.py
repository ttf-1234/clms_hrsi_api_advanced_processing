import os
import zipfile

class Unzipper:
    def __init__(self, config):
        self.config = config

    def unzip_and_cleanup(self):
        print("Starting unzip and cleanup process...")
        project_root = os.getcwd()
        for raster_entry in self.config.reference_rasters:
            raster_folder = os.path.splitext(raster_entry["name"])[0]
            for product_type in self.config.clms_product:
                product_dir = os.path.join(project_root, self.config.output_path_original, raster_folder, product_type)
                if not os.path.isdir(product_dir):
                    print(f"Directory not found: {product_dir}")
                    continue
                print(f"\n=== Unzipping for reference raster: {raster_folder}, product: {product_type} ===")
                for fname in os.listdir(product_dir):
                    if fname.endswith(".zip"):
                        zip_path = os.path.join(product_dir, fname)
                        try:
                            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                zip_ref.extractall(product_dir)
                            print(f"Unzipped: {zip_path}")
                            os.remove(zip_path)
                            print(f"Deleted: {zip_path}")
                        except Exception as e:
                            print(f"Error processing {zip_path}: {e}")
        print("Unzip and cleanup process finished.")