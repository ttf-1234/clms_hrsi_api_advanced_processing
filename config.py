import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

##### Directory containing reference rasters #####
reference_raster_dir = os.path.join(BASE_DIR, "data/reference_raster")


# List your reference rasters here: just the filename and the CRS string.
# The path will be constructed automatically from reference_raster_dir.
# Example: {"name": "dem_rofental_100.asc", "crs": "EPSG:32632"}
reference_rasters = [
    {"name": "dem_rofental_100.asc", "crs": "EPSG:32632"},
    {"name": "dem_guadalfeo_100.asc", "crs": "EPSG:32630"},
    # Add more as needed
]

# Helper to get full path for a reference raster entry
def get_reference_raster_path(raster_entry):
    return os.path.join(reference_raster_dir, raster_entry["name"])

##### CLMS credentials #####
clms_username = "xx"
clms_password = "xx"

##### CLMS product ID #####
clms_query_type = "query_and_download"  # Options: "query", "download", "query_and_download"
# ALLOWED_PRODUCTS = ["FSC", "PSA", "SWS", "WDS", "GFSC"]
clms_product=["FSC"]

##### Period #####
start_date = "2023-07-01T00:00:00Z"
end_date = "2023-07-15T23:59:59Z"

##### Output path for downloaded data #####
output_path_original = os.path.join(BASE_DIR, "data/clms_data/original/")
output_path_processed = os.path.join(BASE_DIR, "data/clms_data/processed/")

##### Further processing #####
mosaic_output = True
reclassify = True
crop_resample = True
filter_cc = False
cc_threshold = 0.2
