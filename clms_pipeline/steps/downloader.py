import os
import requests
import sys
import re
import shutil

class Downloader:
    def __init__(self, config):
        self.config = config

    def download_clms_downloader(self):
        url = "https://raw.githubusercontent.com/eea/clms-hrsi-api-client-python/refs/heads/main/clms_hrsi_downloader.py"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_path = os.path.join(script_dir, "CLMS_downloader.py")
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            print("CLMS_downloader.py already exists and is verified.")
            return local_path
        response = requests.get(url)
        with open(local_path, "wb") as f:
            f.write(response.content)
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            print("CLMS_downloader.py was successfully downloaded and verified.")
            return local_path
        else:
            print("Download failed or file is empty!")
            return None

    def delete_clms_data(self):
        # Delete all contents of data/clms_data/original and data/clms_data/processed before running
        project_root = os.getcwd()
        original_dir = os.path.join(project_root, "data/clms_data/original")
        processed_dir = os.path.join(project_root, "data/clms_data/processed")
        for folder in [original_dir, processed_dir]:
            if os.path.exists(folder):
                print(f"Deleting all contents in: {folder}")
                shutil.rmtree(folder)
                os.makedirs(folder, exist_ok=True)
            else:
                os.makedirs(folder, exist_ok=True)

    def download(self):
        print("Starting CLMS data download...")
        self.delete_clms_data()
        clms_downloader_path = self.download_clms_downloader()
        if clms_downloader_path is None:
            print("Cannot proceed without CLMS_downloader.py.")
            return

        # --- Ensure clms_data directory exists ---
        base_dir = os.path.dirname(self.config.__file__) if hasattr(self.config, "__file__") else os.getcwd()
        clms_data_dir = os.path.join(base_dir, "data/clms_data")
        os.makedirs(clms_data_dir, exist_ok=True)

        # --- Ensure credentials file exists ---
        credentials_path = os.path.join(clms_data_dir, "credentials.txt")
        if not os.path.exists(credentials_path):
            with open(credentials_path, "w") as f:
                f.write(f"{self.config.clms_username}:{self.config.clms_password}\n")
            print(f"Created credentials file at {credentials_path}")
        else:
            print(f"Credentials file already exists at {credentials_path}")
            with open(credentials_path, "r") as f:
                line = f.readline().strip()
            if ':' not in line or not all(line.split(':')):
                print(f"Credentials file at {credentials_path} is incomplete or malformed. Recreating...")
                with open(credentials_path, "w") as f:
                    f.write(f"{self.config.clms_username}:{self.config.clms_password}\n")

        ALLOWED_PRODUCTS = ["FSC", "PSA", "SWS", "WDS", "GFSC"]
        ALLOWED_QUERY_TYPES = ["query", "download", "query_and_download"]

        def is_valid_date(date_str):
            pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
            return bool(re.match(pattern, date_str))

        start_date = getattr(self.config, "start_date", None)
        end_date = getattr(self.config, "end_date", None)
        product_types = getattr(self.config, "clms_product", [])
        output_path = getattr(self.config, "output_path_original", None)
        query_type = getattr(self.config, "clms_query_type", None)
        reference_rasters = getattr(self.config, "reference_rasters", [])

        invalid_products = [p for p in product_types if p not in ALLOWED_PRODUCTS]
        if invalid_products:
            print(f"Invalid product types found: {invalid_products}")
            print(f"Allowed products are: {ALLOWED_PRODUCTS}")
            return

        if not is_valid_date(start_date):
            print(f"Start date format invalid: {start_date}")
            print("Expected format: YYYY-MM-DDTHH:MM:SSZ")
            return
        if not is_valid_date(end_date):
            print(f"End date format invalid: {end_date}")
            print("Expected format: YYYY-MM-DDTHH:MM:SSZ")
            return
        if query_type not in ALLOWED_QUERY_TYPES:
            print(f"Invalid query type: {query_type}")
            print(f"Allowed query types are: {ALLOWED_QUERY_TYPES}")
            return

        def get_raster_folder_name(raster_entry):
            return os.path.splitext(raster_entry["name"])[0]

        for raster_entry in reference_rasters:
            raster_folder = get_raster_folder_name(raster_entry)
            tile_file = os.path.join(os.getcwd(), "data/tile_system", f"relevant_tiles_{raster_folder}.txt")
            if not os.path.exists(tile_file):
                print(f"Tile txt file not found for raster {raster_folder}: {tile_file}")
                continue
            with open(tile_file, 'r') as f:
                tile_names = [line.strip() for line in f if line.strip()]
            if not tile_names:
                print(f"No tile names found in the txt file for raster {raster_folder}.")
                continue

            for tile in tile_names:
                print(f"\n=== Processing reference raster: {raster_entry['name']} (folder: {raster_folder}) ===")
                print(f"--- Working on tile: {tile} ---")
                for product_type in product_types:
                    product_output_dir = os.path.join(output_path, raster_folder, product_type)
                    os.makedirs(product_output_dir, exist_ok=True)
                    print(f"Creating product output directory: {product_output_dir}")
                    cmd = (
                        f"python {clms_downloader_path} "
                        f"-{query_type} "
                        f"-productIdentifier {tile} "
                        f"-productType {product_type} "
                        f"-obsDateMin {start_date} "
                        f"-obsDateMax {end_date} "
                        f"-hrsi_credentials {credentials_path} "
                        f"{product_output_dir}"
                    )
                    print(f"Running: {cmd}")
                    os.system(cmd)
                    result_file = os.path.join(product_output_dir, "result_file.txt")
                    new_result_file = os.path.join(product_output_dir, f"result_file_{tile}_{product_type}.txt")
                    if os.path.exists(result_file):
                        os.rename(result_file, new_result_file)
                        print(f"Renamed {result_file} to {new_result_file}")
                    else:
                        print(f"Warning: {result_file} not found after download.")
